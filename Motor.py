from Phidget22.Devices.RCServo import *
from Phidget22.Devices.DCMotor import *

from Device_Manager import Device


class DCMotorDevice(Device):
    def __init__(self, DC_MOTOR_HUB, DC_MOTOR_PORT):
        motor_ch = DCMotor()
        motor_ch.setDeviceSerialNumber(DC_MOTOR_HUB)
        motor_ch.setHubPort(DC_MOTOR_PORT)
        super(DCMotorDevice, self).__init__(motor_ch)

    def on_attach(self):
        self.ch.setCurrentLimit(15.0)


class ServoMotorDevice(Device):
    def __init__(self, SERVO_HUB, SERVO_PORT, SERVO_CHANNEL):
        servo_ch = RCServo()
        servo_ch.setDeviceSerialNumber(SERVO_HUB)
        servo_ch.setHubPort(SERVO_PORT)
        servo_ch.setChannel(SERVO_CHANNEL)
        super(ServoMotorDevice, self).__init__(servo_ch)

    def on_attach(self):
        servo_ch = self.ch
        servo_ch.setMinPulseWidth(500.0)
        servo_ch.setMaxPulseWidth(2500.0)
        servo_ch.setTargetPosition(90)
        servo_ch.setEngaged(1)
