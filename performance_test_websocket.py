#!/usr/bin/env python
import asyncio
import websockets
import time
import json
import requests
import numpy as np
from collections import deque


async def consume_websocket(duration=5, hostname="localhost", port=8080):
    imu_delays = deque()
    _counter = 0
    endpoint = "/ws/imu"
    async with websockets.connect(
        f"ws://{hostname}:{port}{endpoint}"
    ) as websocket:
        print(f"connecting to {endpoint}")
        t_start = time.time()
        while time.time() < t_start + duration:
            message = await websocket.recv()
            _data = json.loads(message)
            imu_delays.append(time.time() - _data["i_utc"])
            _counter += 1
    t_stop = time.time()
    _connection_count = requests.get(
        f"http://{hostname}:{port}/api/websocket_connections"
    ).json()
    _mean_delay = np.mean(imu_delays)
    print(
        f"{_counter} messages received within {duration} s "
        f"({_counter/duration:.2f} Hz, {_connection_count} ws connections, "
        f"avg. delay {_mean_delay:.3f}s)"
    )


asyncio.run(consume_websocket())
