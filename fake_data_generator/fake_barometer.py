#!/usr/bin/env python3
import time
import socket
import numpy as np


class FakeBarometer:
    def __init__(self, i2c_address=0x1D, config_path=None):
        self.hostname = socket.gethostname()

    def get_sensor_data(self):
        timestamp = time.time()
        pressure = (
            101325
            + 2e2 * np.cos(timestamp / 10)
            + 2e3 * np.cos(timestamp / 1e4)
        )
        temperature = 15 + 10 * np.cos(timestamp / 2e3)
        sensor_data = {
            "hostname": self.hostname,
            "p_utc": round(timestamp, 3),
            "pressure": round(pressure, 1),
            "temperature": round(temperature, 1),
        }
        return sensor_data
