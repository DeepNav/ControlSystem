import time
from Spatial import SpatialDevice
from DeviceManager import DeviceManager

def test_spatial():
    dm = DeviceManager()
    dm.add("spatial", SpatialDevice())
    dm.waitUntilAllReady()
    while True:
        print(dm.get_event())
        time.sleep(1)

test_spatial()