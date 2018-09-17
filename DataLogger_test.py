import os
import time
from DataLogger import DataLogger

def get_image_file_name ():
    ts = time.time()
    return ts, ('%.6f' % ts) + ".jpg"

state = {
    "direction": 130.32,
    "throttle": 0.8,
    "lat": 123.21123234,
    "is_manual_mode": False
}
state["timestamp"], state["image_file_name"] = get_image_file_name()
dl = DataLogger(os.getcwd() + "/demo.csv")
dl.write(state)
state["timestamp"], state["image_file_name"] = get_image_file_name()
dl.write(state)
state["timestamp"], state["image_file_name"] = get_image_file_name()
dl.write(state)
