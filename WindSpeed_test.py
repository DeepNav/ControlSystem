import time
from WindSpeed import WindSpeedDevice
from DeviceManager import DeviceManager

def test_WindSpeed():
    dm = DeviceManager()
    dm.add("wind_speed", WindSpeedDevice(529516, 5))
    dm.waitUntilAllReady()
    while True:
        print(dm.get_event())
        time.sleep(1)

test_WindSpeed()