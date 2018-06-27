import pygame
import platform
import os
import threading

from numpy import interp

pygame.init()

class Joystick(object):
    def __init__(self):
        # get pygame ready
        os.putenv('DISPLAY', ':0.0')
        pygame.display.set_mode((1, 1))
        js = pygame.joystick.Joystick(0)
        js.init()

        self.is_forward = 1

        self.is_manual_mode = True
        self.throttle = 0.0
        self.direction = 90
        self.should_exit = False

        self.event = {}

        self.key_mapping = self.get_key_mapping()

        self.start_loop()

    def get_key_mapping(self):
        if platform.system() == "Darwin":
            # mac with wired controller
            return {
                "SWITCH_MODE_BTN": 10,
                "STOP_BTN": 12,
                "STEER_AXIS": 0,
                "THROTTLE_AXIS": 5,
                "GEAR_CHANGE_AXIS": 3,
            }
        elif platform.system() == "Linux":
            # raspberry pi
            return {
                "SWITCH_MODE_BTN": 8,
                "STOP_BTN": 1,
                "STEER_AXIS": 0,
                "THROTTLE_AXIS": 5,
                "GEAR_CHANGE_AXIS": 4,
            }

    def get_event(self):
        return self.event
    
    def start_loop(self):
        js = self
        def event_loop():
            js.event = {}
            for ev in pygame.event.get(pygame.JOYAXISMOTION):
                if ev.axis == js.key_mapping["STEER_AXIS"]:
                    js.direction = interp(ev.value, [-1, 1], [0, 180])
                    js.event["direction"] = js.direction
                if ev.axis == js.key_mapping["GEAR_CHANGE_AXIS"]:
                    if ev.value < (-0.7):
                        js.is_forward = 1
                    elif ev.value > (0.7):
                        js.is_forward = -1
                if ev.axis == js.key_mapping["THROTTLE_AXIS"]:
                    js.throttle = ( interp(ev.value, [-1, 1], [0, 1]) ) * js.is_forward
                    js.event["throttle"] = js.throttle
            for ev in pygame.event.get(pygame.JOYBUTTONDOWN):
                print("button pressed:", ev.button)
                if ev.button == js.key_mapping["STOP_BTN"]:
                    js.should_exit = True
                    js.event["should_exit"] = js.should_exit
                if ev.button == js.key_mapping["SWITCH_MODE_BTN"]:
                    js.is_manual_mode = not js.is_manual_mode
                    js.event["is_manual_mode"] = js.is_manual_mode

        loop_thread = threading.Thread(
            target=event_loop
        )
        loop_thread.daemon = True
        loop_thread.start()
