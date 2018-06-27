import sys
import time
import os
import platform
import logging

from numpy import interp

from Phidget22.Devices.RCServo import *
from Phidget22.Devices.DCMotor import *
from Phidget22.Devices.GPS import *
from Phidget22.PhidgetException import *

import pygame
from Device_Manager import Device_Manager, Device
from Joystick import Joystick


DC_MOTOR_PORT = 0
SERVO_MOTOR_PORT = 1
SERVO_MOTOR_CHANNEL = 15
HUB_SERIAL_NUM = 529516

def init_dc_motor():
    motor_ch = DCMotor()
    motor_ch.setDeviceSerialNumber(HUB_SERIAL_NUM)
    motor_ch.setHubPort(DC_MOTOR_PORT)
    motor_ch.setChannel(0)
    motor_ch.setCurrentLimit(15.0)
    motor = Device(motor_ch)
    motor.is_stable = True
    return motor

def init_servo():
    servo_ch = RCServo()
    servo_ch.setDeviceSerialNumber(HUB_SERIAL_NUM)
    servo_ch.setHubPort(SERVO_MOTOR_PORT)
    servo_ch.setChannel(SERVO_MOTOR_CHANNEL)
    servo_ch.setMinPulseWidth(500.0)
    servo_ch.setMaxPulseWidth(2500.0)
    servo_ch.setTargetPosition(90)
    servo_ch.setEngaged(1)
    return Device(servo_ch)

def init_gps():
    ch = GPS()
    ch.setDeviceSerialNumber(112233)
    gps = Device(ch)
    gps.is_stable = False

    def on_fix_change(self, positionFixState):
        gps.is_stable = positionFixState
    
    def on_heading_change(self, heading, velocity):
        logging.info("heading changed heading: %f, velocity: %f", heading, velocity)
    
    def on_position_change(self, latitude, longitude, altitude):
        logging.info("postion changed lat: %f, lon: %f, alt: %f", latitude, longitude, altitude)
    
    ch.setOnPositionFixStateChangeHandler(on_fix_change)
    ch.setOnPositionChangeHandler(on_position_change)
    ch.setOnHeadingChangeHandler(on_heading_change)

    return gps

def setup():
    dm = Device_Manager()
    js = Joystick()

    dc_motor = init_dc_motor()
    dm.add("dc_motor", dc_motor)

    dm.link("dc_motor", "setTargetVelocity", "throttle")

    servo = init_servo()
    dm.add("servo", servo)
    dm.link("servo", "setTargetPosition", "direction")

    gps = init_gps()
    dm.add("gps", gps)

    dm.waitUntilAllReady()

    return dm, js

def fetch_ai_command():
    return {
        "throttle": 0.2,
        "direction": 30
    }

def main():
    state = {
       "should_exit": False,
       "is_manual_mode": True,
    }

    dm, js = setup()
    
    while not state["should_exit"]:
        state.update(js.get_event())
        if state["should_exit"]:
            continue
        if state["is_manual_mode"]:
            dm.batch_update(js.get_event())
        else:
            dm.batch_update(fetch_ai_command())
            
