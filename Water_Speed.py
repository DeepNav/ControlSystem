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
        
        def on_frequency_change(ch, frequency):
            water_speed = self.get_water_speed(frequency)
            self.set_event_val(self.event_key_name, water_speed)

        ch.setOnFrequencyChangeHandler(on_frequency_change)
    
    def get_water_speed(self, frequency):
        # f = Q*7.5, Q is the flowspeed in L/min
        flowspeed = (frequency/7.5) / 60000 # L/min to m3/s
        return flowspeed / SECTIONAL_AREA
    
    def on_attach(self):
        self.ch.setDataInterval(500)

