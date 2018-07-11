import logging

from lidar_lite.LidarLite import LidarLite
from Device_Manager import Device


class LidarLiteDevice(Device):
    def __init__(self):
        ch = LidarLite()
        super(LidarLiteDevice, self).__init__(ch)

    def on_attach(self):
        lidar = self

        def on_distance_change(new_val, old_val):
            logging.debug("LidarDevice: distance changed to %d", new_val)
            lidar.set_event_val("lidar_distance", new_val)
        self.listen("DistanceChange", on_distance_change)
