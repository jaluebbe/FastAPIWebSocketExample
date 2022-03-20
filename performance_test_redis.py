#!/usr/bin/env python3
import redis
import json
import numpy as np
from collections import deque
import time

redis_connection = redis.Redis(decode_responses=True)
imu_delays = deque()
duration = 2
_counter = 0
print("subscribing imu")
_pubsub = redis_connection.pubsub()
_pubsub.subscribe("imu")
t_start = time.time()
for item in _pubsub.listen():
    if time.time() > t_start + duration:
        break
    if not item["type"] == "message":
        continue
    _data = json.loads(item["data"])
    imu_delays.append(time.time() - _data["i_utc"])
    _counter += 1
t_stop = time.time()
_connection_count = redis_connection.get("ws_connections")
_mean_delay = np.mean(imu_delays)
print(
    f"{_counter} messages received within {duration} s ({_counter/duration:.2f}"
    f" Hz, {_connection_count} ws connections, avg. delay {_mean_delay:.3f}s)"
)
