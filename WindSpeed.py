from Phidget22.Devices.FrequencyCounter import *

from DeviceManager import Device


class WindSpeedDevice(Device):
    def __init__(self, WIND_HUB, WIND_SPEED_PORT):
        ch = FrequencyCounter()
        ch.setDeviceSerialNumber(WIND_HUB)
        ch.setHubPort(WIND_SPEED_PORT)
        super(WindSpeedDevice, self).__init__(ch)

    def on_attach(self):
        device = self

        def on_frequency_change(ch, frequency):
            # wind speed (mph) = frequency * 1.492
            device.set_event_val("wind_speed", frequency * 1.492)

        self.ch.setDataInterval(500)
        self.listen("FrequencyChange", on_frequency_change)
