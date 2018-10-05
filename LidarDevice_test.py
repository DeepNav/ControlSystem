import time
from LidarDevice import LidarLiteDevice
from DeviceManager import DeviceManager

def test_lidar():
    dm = DeviceManager()
    dm.add("lidar", LidarLiteDevice())
    dm.waitUntilAllReady()
    while True:
        print(dm.get_event())
        time.sleep(1)

test_lidar()