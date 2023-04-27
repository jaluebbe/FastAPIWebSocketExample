from fastapi import FastAPI, HTTPException, WebSocket, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from redis import asyncio as aioredis
import json
import os
import asyncio
import logging

if "REDIS_HOST" in os.environ:
    redis_host = os.environ["REDIS_HOST"]
else:
    redis_host = "127.0.0.1"
redis_connection = aioredis.Redis(host=redis_host, decode_responses=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


async def _get_channel_data(channel):
    pubsub = redis_connection.pubsub(ignore_subscribe_messages=True)
    await pubsub.subscribe(channel)
    while True:
        message = await pubsub.get_message()
        if message is not None:
            _channel = message["channel"]
            _data = json.loads(message["data"])
            _data["channel"] = _channel
            return _data
        await asyncio.sleep(0.01)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/static/index.html")


@app.get("/api/websocket_connections")
async def get_websocket_connections():
    websocket_connections = await redis_connection.get("ws_connections")
    return websocket_connections


@app.get("/api/current_orientation")
async def get_current_orientation():
    channel = "imu"
    try:
        imu_data = await asyncio.wait_for(_get_channel_data(channel), 0.2)
    except asyncio.TimeoutError:
        logging.exception("/api/current_orientation")
        raise HTTPException(status_code=404, detail="no data available")
    return imu_data


@app.get("/api/current_pressure")
async def get_current_pressure():
    channel = "barometer"
    try:
        baro_data = await asyncio.wait_for(_get_channel_data(channel), 0.2)
    except asyncio.TimeoutError:
        logging.exception("/api/current_pressure")
        raise HTTPException(status_code=404, detail="no data available")
    return baro_data


async def redis_connector(
    websocket: WebSocket, source_channel: str, target_channel: str
):
    async def consumer_handler(
        redis_connection: aioredis.client.Redis,
        websocket: WebSocket,
        target_channel: str,
    ):
        async for message in websocket.iter_text():
            await redis_connection.publish(target_channel, message)

    async def producer_handler(
        pubsub: aioredis.client.PubSub,
        websocket: WebSocket,
        source_channel: str,
    ):
        await pubsub.subscribe(source_channel)
        async for message in pubsub.listen():
            await websocket.send_text(message["data"])

    redis_connection = aioredis.Redis(host=redis_host, decode_responses=True)
    pubsub = redis_connection.pubsub(ignore_subscribe_messages=True)
    ws_connections = await redis_connection.incr("ws_connections")
    await redis_connection.publish("ws_connections", ws_connections)
    consumer_task = consumer_handler(
        redis_connection, websocket, target_channel
    )
    producer_task = producer_handler(pubsub, websocket, source_channel)
    done, pending = await asyncio.wait(
        [consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED
    )
    logging.debug(f"Done task: {done}")
    for task in pending:
        logging.debug(f"Cancelling task: {task}")
        task.cancel()
    ws_connections = await redis_connection.decr("ws_connections")
    await redis_connection.publish("ws_connections", ws_connections)
    await redis_connection.close()


@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    supported_channels = ["imu", "barometer", "ws_connections", "imu_pressure"]
    await websocket.accept()
    if channel not in supported_channels:
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
        return
    await redis_connector(
        websocket, source_channel=channel, target_channel="client_feedback"
    )
