#!/usr/bin/env python3
import time
import os
import json
import redis
from fake_imu import FakeImu
from fake_barometer import FakeBarometer


if __name__ == "__main__":

    if "REDIS_HOST" in os.environ:
        redis_host = os.environ["REDIS_HOST"]
    else:
        redis_host = "127.0.0.1"
    redis_connection = redis.Redis(host=redis_host)
    imu = FakeImu()
    barometer = FakeBarometer()
    while True:
        sensor_data = imu.get_sensor_data()
        sensor_data["channel"] = "imu"
        redis_connection.publish(
            sensor_data["channel"], json.dumps(sensor_data)
        )
        sensor_data = barometer.get_sensor_data()
        sensor_data["channel"] = "barometer"
        redis_connection.publish(
            sensor_data["channel"], json.dumps(sensor_data)
        )
        time.sleep(0.04)
