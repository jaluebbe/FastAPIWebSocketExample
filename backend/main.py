from fastapi import FastAPI, HTTPException, WebSocket, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import aioredis
import websockets
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

templates = Jinja2Templates(directory="templates")


async def _get_channel_data(channels):
    pubsub = redis_connection.pubsub(ignore_subscribe_messages=True)
    await pubsub.subscribe(channels)
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


@app.get("/threejs.html", response_class=HTMLResponse)
async def threejs(request: Request):
    return templates.TemplateResponse(
        "threejs.html",
        {
            "request": request,
            "my_host": request.url.hostname,
            "my_port": request.url.port,
        },
    )


@app.get("/websocket_consumer.js", response_class=HTMLResponse)
async def websocket_consumer(request: Request):
    return templates.TemplateResponse(
        "websocket_consumer.js",
        {
            "request": request,
            "my_host": request.url.hostname,
            "my_port": request.url.port,
        },
    )


@app.get("/api/current_orientation")
async def get_current_orientation():
    channels = ["imu"]
    try:
        imu_data = await asyncio.wait_for(_get_channel_data(channels), 0.2)
    except asyncio.TimeoutError:
        logging.exception("/api/current_orientation")
        raise HTTPException(status_code=404, detail="no data available")
    return imu_data


@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    supported_channels = ["imu"]
    await websocket.accept()
    if channel not in supported_channels:
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
        return
    pubsub = redis_connection.pubsub(ignore_subscribe_messages=True)
    await pubsub.subscribe([channel])
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
