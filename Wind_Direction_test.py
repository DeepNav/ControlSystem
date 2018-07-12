import time
from Wind_Direction import WindDirectionDevice
from Device_Manager import Device_Manager

def test_direction():
    dm = Device_Manager()
    dm.add("wind_direction", WindDirectionDevice(529470, 0))
    dm.waitUntilAllReady()
    while True:
        print(dm.get_event())
        time.sleep(1)

test_direction()