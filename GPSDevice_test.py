import time
from GPSDevice import GPSDevice
from DeviceManager import DeviceManager

def test_GPS():
    dm = DeviceManager()
    dm.add("gps", GPSDevice(285225))
    dm.waitUntilAllReady()
    while True:
        print(dm.get_event())
        time.sleep(1)

test_GPS()