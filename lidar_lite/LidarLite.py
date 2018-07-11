import serial
import logging
import threading

from usb_port_finder import wait_until_arduino_connected


class LidarLite(object):
    def __init__(self):
        self.should_stop = False
        self.val = None
        self.onDistanceChange = None
        self.OnAttach = None
        self.OnDetach = None
        self.OnError = None
        self.ser = None

    def start_pulling_data(self):
        if self.ser is None:
            logging.warning("Lidar Device is not attached")
            self.open()
        while not self.should_stop:
            new_val = self.ser.readline()
            if new_val != self.val:
                old_val = self.val
                self.val = new_val
                if self.onDistanceChange is not None:
                    self.onDistanceChange(new_val, old_val)

    def setOnDistanceChangeHandler(self, fn):
        self.onDistanceChange = fn

    def setOnAttachHandler(self, fn):
        self.OnAttach = fn

    def setOnDetachHandler(self, fn):
        self.OnDetach = fn

    def setOnErrorHandler(self, fn):
        self.OnError = fn

    def open(self):
        logging.info("waiting for arduino to connect")
        port = wait_until_arduino_connected()
        self.ser = serial.Serial(port, 9600)

        t = threading.Thread(
            target=self.start_pulling_data
        )
        t.daemon = True
        self.OnAttach(self)
        t.start()
        logging.info("Lidar's arduino is connected")
