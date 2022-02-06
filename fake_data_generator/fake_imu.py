#!/usr/bin/env python3
import time
import os
import json
import socket
import redis
import numpy as np


class FakeImu:
    def __init__(self, i2c_address=0x1D, config_path=None):
        self.hostname = socket.gethostname()

    def get_sensor_data(self):
        timestamp = time.time()
        roll = 60 * np.cos(timestamp / 2)
        pitch = 45 * np.cos(timestamp / 10)
        yaw = 180 * np.cos(timestamp / 20)
        sensor_data = {
            "hostname": self.hostname,
            "i_utc": round(timestamp, 3),
            "roll": round(roll, 1),
            "pitch": round(pitch, 1),
            "yaw": round(yaw, 1),
        }
        return sensor_data


if __name__ == "__main__":

    if "REDIS_HOST" in os.environ:
        redis_host = os.environ["REDIS_HOST"]
    else:
        redis_host = "127.0.0.1"
    redis_connection = redis.Redis(host=redis_host)
    sensor = FakeImu()
    while True:
        sensor_data = sensor.get_sensor_data()
        redis_connection.publish("imu", json.dumps(sensor_data))
        time.sleep(0.04)
