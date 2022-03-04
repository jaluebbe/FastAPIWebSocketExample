from fastapi import FastAPI, HTTPException, WebSocket, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import aioredis
import websockets.exceptions
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
    return FileResponse("index.html")


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
    channels = "barometer"
    try:
        baro_data = await asyncio.wait_for(_get_channel_data(channel), 0.2)
    except asyncio.TimeoutError:
        logging.exception("/api/current_pressure")
        raise HTTPException(status_code=404, detail="no data available")
    return baro_data


@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    supported_channels = ["imu", "barometer"]
    await websocket.accept()
    if channel not in supported_channels:
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
        return
    pubsub = redis_connection.pubsub(ignore_subscribe_messages=True)
    await pubsub.subscribe(channel)
    while True:
        try:
            message = await pubsub.get_message()
            if message is not None:
                await websocket.send_text(message["data"])
            await asyncio.sleep(0.01)
        except asyncio.TimeoutError:
            pass
        except websockets.exceptions.ConnectionClosedError:
            logging.exception("abnormal closure of websocket connection.")
            break
        except websockets.exceptions.ConnectionClosedOK:
            # normal closure with close code 1000
            break
