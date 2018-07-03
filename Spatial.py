import math
import logging

from Phidget22.Devices.Spatial import *
from Device_Manager import Device


class SpatialDevice(Device):
    def __init__(self):
        self.ch = Spatial()
        super(SpatialDevice, self).__init__(self.ch)
        self.ch.setOnSpatialDataHandler(self.__on_data)

        self.last_angles = [0.0, 0.0, 0.0]
        self.compass_bearing_filter = []
        self.bearing_filter_size = 2
        self.compass_bearing = 0
    
    def on_attach(self):
        self.ch.setDataInterval(500)

    def __on_data(self, ch, acceleration, angularRate, magneticField, timestamp):
        self.CalculateBearing(acceleration, angularRate,
                              magneticField, timestamp)
        self.set_event_val("acc_x", acceleration[0])
        self.set_event_val("acc_y", acceleration[1])
        self.set_event_val("acc_z", acceleration[2])

        self.set_event_val("ang_x", angularRate[0])
        self.set_event_val("ang_y", angularRate[1])
        self.set_event_val("ang_z", angularRate[2])

        self.set_event_val("mag_x", magneticField[0])
        self.set_event_val("mag_y", magneticField[1])
        self.set_event_val("mag_z", magneticField[2])

    def CalculateBearing(self, acceleration, angularRate, magneticField, timestamp):

        gravity = acceleration
        mag_field = magneticField
        angles = []

        roll_angle = math.atan2(gravity[1], gravity[2])

        pitch_angle = math.atan(-gravity[0] / (gravity[1] * math.sin(
            roll_angle) + gravity[2] * math.cos(roll_angle)))

        yaw_angle = math.atan2(mag_field[2] * math.sin(roll_angle) - mag_field[1] * math.cos(roll_angle), mag_field[0] * math.cos(
            pitch_angle) + mag_field[1] * math.sin(pitch_angle) * math.sin(roll_angle) + mag_field[2] * math.sin(pitch_angle) * math.cos(roll_angle))

        angles.append(roll_angle)
        angles.append(pitch_angle)
        angles.append(yaw_angle)

        try:
            for i in xrange(0, 3, 2):
                if math.fabs(angles[i] - self.last_angles[i] > 3):
                    for stuff in self.compass_bearing_filter:
                        if angles[i] > self.last_angles[i]:
                            stuff[i] += 360 * math.pi / 180.0
                        else:
                            stuff[i] -= 360 * math.pi / 180.0

            self.last_angles = angles
            self.compass_bearing_filter.append(angles)
            if len(self.compass_bearing_filter) > self.bearing_filter_size:
                self.compass_bearing_filter.pop(0)

            yaw_angle = pitch_angle = roll_angle = 0

            for stuff in self.compass_bearing_filter:
                roll_angle += stuff[0]
                pitch_angle += stuff[1]
                yaw_angle += stuff[2]

            yaw_angle = yaw_angle / len(self.compass_bearing_filter)
            pitch_angle = pitch_angle / len(self.compass_bearing_filter)
            roll_angle = roll_angle / len(self.compass_bearing_filter)

            # Convert radians to degrees for display
            self.compass_bearing = yaw_angle * (180.0 / math.pi) % 360
            self.set_event_val("compass_bearing", round(self.compass_bearing, 3))
            self.set_event_val("pitch_angle", round(pitch_angle* (180.0 / math.pi), 3))
            self.set_event_val("roll_angle", round(roll_angle* (180.0 / math.pi), 3))
        except Exception as e:
            logging.error(e)
