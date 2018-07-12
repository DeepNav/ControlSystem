import time
import logging
import threading

from numpy import interp

from Phidget22.Devices.RCServo import *
from Phidget22.Devices.DCMotor import *
from Phidget22.Devices.GPS import *
from Phidget22.PhidgetException import *
from Phidget22.Devices.FrequencyCounter import *

from DeviceManager import DeviceManager, Device
from Joystick import Joystick
from WsServer import WsServer
from Spatial import SpatialDevice
from WindDirection import WindDirectionDevice
from WaterSpeed import WaterSpeedDevice
from Motor import DCMotorDevice, ServoMotorDevice
from GPSDevice import GPSDevice
from WindSpeed import WindSpeedDevice
from LidarDevice import LidarLiteDevice

logging.basicConfig(level=logging.INFO)

WS_PORT = 8000

HUB_0 = 529516
HUB_1 = 529470
GPS_SERIAL_NUM = 285225

DC_MOTOR_HUB = HUB_0
DC_MOTOR_PORT = 0

SERVO_HUB = HUB_0
SERVO_PORT = 1
SERVO_CHANNEL = 0

SPATIAL_HUB = HUB_0
SPATIAL_PORT = 2

WIND_HUB = HUB_0
WIND_SPEED_PORT = 3
WIND_DIRECTION_PORT = 4

WATER_SPEED_HUB = HUB_1
WATER_SPEED_FORWARD_PORT = 0
WATER_SPEED_BACKWARD_PORT = 1
WATER_SPEED_LEFT_PORT = 2
WATER_SPEED_RIGHT_PORT = 3


def hardware_setup():
    dm = DeviceManager()
    js = Joystick()

    dm.add("dc_motor", DCMotorDevice(DC_MOTOR_HUB, DC_MOTOR_PORT))
    dm.link("dc_motor", "setTargetVelocity", "throttle")

    dm.add("servo", ServoMotorDevice(SERVO_HUB, SERVO_PORT, SERVO_CHANNEL))
    dm.link("servo", "setTargetPosition", "direction",
            lambda val: interp(val, [0, 180], [45, 135]))

    dm.add("gps", GPSDevice(GPS_SERIAL_NUM))

    dm.add("wind_speed", WindSpeedDevice(WIND_HUB, WIND_SPEED_PORT))
    dm.add("wind_direction", WindDirectionDevice(
        WIND_HUB, WIND_DIRECTION_PORT))

    dm.add("spatial", SpatialDevice())

    dm.add("water_speed_forward", WaterSpeedDevice(
        "forward", WATER_SPEED_HUB, WATER_SPEED_FORWARD_PORT))
    dm.add("water_speed_backward", WaterSpeedDevice(
        "backward", WATER_SPEED_HUB, WATER_SPEED_BACKWARD_PORT))
    dm.add("water_speed_left", WaterSpeedDevice(
        "left", WATER_SPEED_HUB, WATER_SPEED_LEFT_PORT))
    dm.add("water_speed_right", WaterSpeedDevice(
        "right", WATER_SPEED_HUB, WATER_SPEED_RIGHT_PORT))

    dm.add("lidar", LidarLiteDevice())

    dm.waitUntilAllReady()

    return dm, js


def start_ws():
    ws_server = WsServer(WS_PORT)
    ws_server_thread = threading.Thread(
        target=ws_server.start_server,
        args=()
    )
    ws_server_thread.daemon = True
    ws_server_thread.start()
    return ws_server


def fetch_ai_command():
    return {
        "throttle": 0.2,
        "direction": 30
    }


def main():
    state = {
        "should_exit": False,
        "is_manual_mode": True,
        "is_cruise_mode": False,
    }

    dm, js = hardware_setup()

    ws_server = start_ws()

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
            ws_server.broadcast(state)
            last_sync_ts = time.time()

        if time.time() - last_ws_ts > 0.1:
            # push delta only every 0.1s if there is any
            event.update(dm.get_event())
            if len(event) > 0:
                ws_server.broadcast(event)
                last_ws_ts = time.time()


main()
