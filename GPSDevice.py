import logging

from Phidget22.Devices.GPS import *

from DeviceManager import Device


class GPSDevice(Device):
    def __init__(self, GPS_SERIAL_NUM):
        ch = GPS()
        ch.setDeviceSerialNumber(GPS_SERIAL_NUM)
        gps = Device(ch)
        gps.is_stable = True
        super(GPSDevice, self).__init__(ch)

    def on_attach(self):
        device = self

        def on_fix_change(ch, positionFixState):
            #gps.is_stable = positionFixState
            pass

        def on_heading_change(ch, heading, velocity):
            logging.debug("heading changed heading: %f, velocity: %f",
                          heading, velocity)
            device.set_event_val("ground_speed", round(velocity, 3))
            device.set_event_val("heading", heading)

        def on_position_change(ch, latitude, longitude, altitude):
            logging.debug("postion changed lat: %f, lon: %f, alt: %f",
                          latitude, longitude, altitude)
            device.set_event_val("lat", round(latitude, 6))
            device.set_event_val("lng", round(longitude, 6))
            device.set_event_val("alt", round(altitude, 2))

        self.listen("PositionFixStateChange", on_fix_change)
        self.listen("PositionChange", on_position_change)
        self.listen("HeadingChange", on_heading_change)
