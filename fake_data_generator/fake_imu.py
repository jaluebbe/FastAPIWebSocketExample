#!/usr/bin/env python3
import time
import socket
import numpy as np


class FakeImu:
    def __init__(self, i2c_address=0x1D, config_path=None):
        self.hostname = socket.gethostname()

    def get_sensor_data(self):
        timestamp = time.time()
        roll = 60 * np.cos(timestamp / 5)
        pitch = 45 * np.cos(timestamp / 10)
        yaw = 180 * np.cos(timestamp / 30)
        sensor_data = {
            "hostname": self.hostname,
            "i_utc": round(timestamp, 3),
            "roll": round(roll, 1),
            "pitch": round(pitch, 1),
            "yaw": round(yaw, 1),
        }
        return sensor_data
