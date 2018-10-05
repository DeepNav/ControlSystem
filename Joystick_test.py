import time
from Joystick import Joystick

js = Joystick()

def test_joystick():
    while True:
        print(js.get_event())
        time.sleep(1)

test_joystick()