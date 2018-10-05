import time
from WaterSpeed import WaterSpeedDevice
from DeviceManager import DeviceManager
import logging

logging.basicConfig(level=logging.DEBUG)

def test_direction():
    dm = DeviceManager()
    print("adding devices")
    dm.add("water_speed_forward", WaterSpeedDevice("forward", 529470, 1))
    dm.add("water_speed_backward", WaterSpeedDevice("backward", 529470, 2))
    dm.add("water_speed_left", WaterSpeedDevice("left", 529470, 3))
    dm.add("water_speed_right", WaterSpeedDevice("right", 529470, 4))
    print("start to wait for device ready")
    dm.waitUntilAllReady()
    print("device ready")
    while True:
        print(dm.get_event())
        time.sleep(1)

test_direction()