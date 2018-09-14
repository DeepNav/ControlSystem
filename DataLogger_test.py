import os
import time
from DataLogger import DataLogger

state = {
    "timestamp": time.time(),
    "direction": 130.32,
    "throttle": 0.8,
    "lat": 123.21123234,
    "is_manual_mode": False,
}
dl = DataLogger(os.getcwd() + "/demo.csv")
dl.write(state)
