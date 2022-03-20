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
    interval = 0.04
    imu = FakeImu()
    barometer = FakeBarometer()
    while True:
        t_start = time.time()
        imu_data = imu.get_sensor_data()
        redis_connection.publish("imu", json.dumps(imu_data))
        barometer_data = barometer.get_sensor_data()
        redis_connection.publish("barometer", json.dumps(barometer_data))
        imu_data.update(barometer_data)
        redis_connection.publish("imu_pressure", json.dumps(imu_data))
        dt = time.time() - t_start
        time.sleep(max(0, interval - dt))
