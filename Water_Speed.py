import logging
import math

from Phidget22.Devices.FrequencyCounter import *
from Device_Manager import Device

DIAMETER = 0.0127
SECTIONAL_AREA = math.pi * math.pow(DIAMETER/2, 2)


class WaterSpeedDevice(Device):
    def __init__(self, water_direction, hub_serial_num, port_num):
        ch = FrequencyCounter()
        ch.setDeviceSerialNumber(hub_serial_num)
        ch.setHubPort(port_num)
        self.event_key_name = "water_speed_" + water_direction
        self.ch = ch

        super(WaterSpeedDevice, self).__init__(ch)

    def get_water_speed(self, frequency):
        # f = Q*7.5, Q is the flowspeed in L/min
        flowspeed = (frequency/7.5) / 60000  # L/min to m3/s
        return flowspeed / SECTIONAL_AREA

    def on_attach(self):
        device = self
        self.ch.setDataInterval(500)

        def on_frequency_change(ch, frequency):
            water_speed = device.get_water_speed(frequency)
            device.set_event_val(device.event_key_name, water_speed)

        self.listen("FrequencyChange", on_frequency_change)
