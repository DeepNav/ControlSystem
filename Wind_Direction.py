import logging

from Phidget22.Devices.VoltageInput import *
from Device_Manager import Device


class WindDirectionDevice(Device):
    def __init__(self, HUB_SERIAL_NUM, PORT_NUM):
        self.v_d_tuples_raw = [
            (3.84, 0.0),
            (1.98, 22.5),
            (2.25, 45.0),
            (0.41, 67.5),
            (0.45, 90.0),
            (0.32, 112.5),
            (0.90, 135.0),
            (0.62, 157.5),
            (1.40, 180.0),
            (1.19, 202.5),
            (3.08, 225.0),
            (2.93, 247.5),
            (4.62, 270.0),
            (4.04, 292.5),
            (4.33, 315.0),
            (3.43, 337.5),
        ]
        self.v_d_tuples = []
        self.init_voltage_range_map()

        self.ch = VoltageInput()
        self.ch.setDeviceSerialNumber(HUB_SERIAL_NUM)
        self.ch.setHubPort(PORT_NUM)

        super(WindDirectionDevice, self).__init__(self.ch)

    def on_attach(self):
        self.ch.setDataInterval(500)
        self.ch.setVoltageChangeTrigger(0.01)
        self.listen("VoltageChange", self.onVoltageChangeHandler)

    def onVoltageChangeHandler(self, ch, voltage):
        logging.debug("voltage changed to %f", voltage)
        self.set_event_val("wind_direction", self.find_direction(voltage))

    def init_voltage_range_map(self):
        self.v_d_tuples_raw = sorted(
            self.v_d_tuples_raw, key=lambda v_d_map: v_d_map[0])

        previous_range_end = 0.0
        for idx, v_d_tuple in enumerate(self.v_d_tuples_raw):
            mid_point = v_d_tuple[0]
            direction = v_d_tuple[1]
            if (idx + 1) == len(self.v_d_tuples_raw):
                next_midpoint = self.v_d_tuples_raw[idx - 1][0]
            else:
                next_midpoint = self.v_d_tuples_raw[idx + 1][0]
            margin = abs((next_midpoint - mid_point)/2)
            range_start = previous_range_end
            range_end = mid_point + margin
            previous_range_end = range_end
            v_range = (range_start, range_end)
            self.v_d_tuples.append((v_range, direction))

    def find_direction(self, voltage):
        for v_range, direction in self.v_d_tuples:
            if v_range[0] < voltage <= v_range[1]:
                return direction
        return None
