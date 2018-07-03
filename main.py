import sys
import time
import os
import platform
import logging
import threading
import json

from numpy import interp

from Phidget22.Devices.RCServo import *
from Phidget22.Devices.DCMotor import *
from Phidget22.Devices.GPS import *
from Phidget22.PhidgetException import *

from Device_Manager import Device_Manager, Device
from Joystick import Joystick
from ws_server import start_ws_server

logging.basicConfig(level=logging.INFO)

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
    ch.setDeviceSerialNumber(285225)
    gps = Device(ch)
    gps.is_stable = False

    def on_fix_change(self, positionFixState):
        gps.is_stable = positionFixState
    
    def on_heading_change(self, heading, velocity):
        logging.debug("heading changed heading: %f, velocity: %f", heading, velocity)
        gps.set_event_val("ground_speed", round(velocity, 3))
        gps.set_event_val("heading", heading)
    
    def on_position_change(self, latitude, longitude, altitude):
        logging.debug("postion changed lat: %f, lon: %f, alt: %f", latitude, longitude, altitude)
        gps.set_event_val("lat", round(latitude, 6))
        gps.set_event_val("lng", round(longitude, 6))
        gps.set_event_val("alt", round(altitude, 2))
    
    ch.setOnPositionFixStateChangeHandler(on_fix_change)
    ch.setOnPositionChangeHandler(on_position_change)
    ch.setOnHeadingChangeHandler(on_heading_change)

    return gps

def setup():
    dm = Device_Manager()
    js = Joystick()
    '''
    dc_motor = init_dc_motor()
    dm.add("dc_motor", dc_motor)

    dm.link("dc_motor", "setTargetVelocity", "throttle")

    servo = init_servo()
    dm.add("servo", servo)
    dm.link("servo", "setTargetPosition", "direction")
'''
    gps = init_gps()
    dm.add("gps", gps)
    
    dm.waitUntilAllReady()

    return dm, js

def fetch_ai_command():
    return {
        "throttle": 0.2,
        "direction": 30
    }

def broadcast_message(msg, clients):
    for client in clients:
        msg.update({
            "ts": time.time()
        })
        client.sendMessage(unicode(json.dumps(msg)))

def main():
    state = {
       "should_exit": False,
       "is_manual_mode": True,
       "is_cruise_mode": False,
    }

    dm, js = setup()

    ws_clients = []

    ws_server_thread = threading.Thread(
        target=start_ws_server,
        args=(ws_clients,)
    )
    ws_server_thread.daemon = True
    ws_server_thread.start()

    logging.info("All services up and running")
    
    last_ws_ts = time.time()
    last_sync_ts = time.time()

    while not state["should_exit"]:
        event = js.get_event()

        # dispatch control command
        if state["is_manual_mode"]:
            if state["is_cruise_mode"]:
                if "direction" in event:
                    event["direction"] = state["direction"]
                if "throttle" in event:
                    event["throttle"] = state["throttle"]
            dm.batch_update(event)
        else:
            ai_command = fetch_ai_command()
            state.update(ai_command)
            event.update(ai_command)
            dm.batch_update(ai_command)
        
        state.update(event)
        if state["should_exit"]:
            continue

        # broadcast state/event to client
        if time.time() - last_sync_ts > 0.5:
            # sync state every 0.5s
            state.update(dm.get_state())
            broadcast_message(state, ws_clients)
            last_sync_ts = time.time()

        if time.time() - last_ws_ts > 0.1:
            # push delta only every 0.1s if there is any
            event.update(dm.get_event())
            if len(event) > 0:
                broadcast_message(event, ws_clients)
                last_ws_ts = time.time()
main()
