import serial
import logging
import threading

from usb_port_finder import wait_until_arduino_connected

'''

How is it connected

LIDAR-Lite v3HP (https://www.sparkfun.com/products/14599) is going to be 
connected via i2c to an Arduino, which is connected to laptop via USB, and 
control system will talk to the Arduino via serial.

Why did we add extra Arduino

LIDAR-Lite v3HP provides 2 date interfaces, i2c or PWM. Currently Phidget does
not have a i2c adaptor, we tried to go the PWM way, but "Versatile Input" is not
fast enough to work with PWM mearsuring; On the other hand, LIDAR-Lite v3HP
also provides a Arduino library to be easy to work with, that's why we go with
extra Arduino in our system

Wiring Guide

Mostly followed https://learn.sparkfun.com/tutorials/lidar-lite-v3-hookup-guide, 
but we skipped getting 5v from Arduino, but from our powerful 5VDC source 
instead, and we do not need the 1000μF capacitor either. the wiring is as:

Lidar Wire        To
Red               Power source 5V
Black             Power source GND And Ardino Power GND
Blue              Arduino SDA
Green             Arduino SCL
Yellow            Leave open
Orange            Leave open

Arduino Code
https://learn.sparkfun.com/tutorials/lidar-lite-v3-hookup-guide

'''


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
