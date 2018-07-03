import threading
import time
import logging

from Phidget22.Phidget import Phidget

class Device(object):
    def __init__(self, ch):
        self.ch = ch
        self.device_id = None
        self.is_attached = False
        self.is_stable = True
        self.event = {}
        self.state = {}
    def is_ready(self):
        return ( self.is_attached and self.is_stable )
    def get_event(self):
        e = self.event
        self.event = {}
        return e
    def get_state(self):
        return self.state
    def set_event_val(self, key, val):
        if (key in self.state and val != self.state[key]) or key not in self.state:
            self.event[key] = val
            self.state[key] = val
    def on_attach(self):
        pass

class Device_Manager(object):
    def __init__(self):
        self.device_repo = {}
        self.event_links = {}
    
    def __device_detached(self, device):
        logging.warn("Device detached: %s", device.device_id)
        device.ch.open()
        device.is_attached = False
        self.waitUntilAllReady()

    def __device_attached(self, device):
        logging.info("Device attached: %s", device.device_id)
        device.is_attached = True
        device.on_attach()

    def __device_error(self, device, errorCode, errorString):
        logging.error("Device error %s, %s", device.device_id, errorString)
        logging.error(errorCode)

    def get(self, id):
        return self.device_repo[id]

    def add(self, id, device):
        logging.info("Device added to dm: %s", id)
        dm = self
        device.device_id = id
        def onAttached(self):
            dm.__device_attached(device)
        def onDetached(self):
            dm.__device_detached(device)
        def onError(self, errorCode, errorString):
            dm.__device_error(device, errorCode, errorString)
        # check if device a phdget device
        if isinstance(device.ch, Phidget):
            self.device_repo[device.device_id] = device
            device.ch.setOnAttachHandler(onAttached)
            device.ch.setOnDetachHandler(onDetached)
            device.ch.setOnErrorHandler(onError)
            device.ch.open()
        else:
            pass

    def waitUntilAllReady(self):
        logging.info("Start to wait for all devices to become ready")
        someone_not_ready = True
        while someone_not_ready:
            someone_not_ready = False
            for id, device in self.device_repo.iteritems():
                if not device.is_ready():
                    logging.info("some device is not ready, keep waiting")
                    someone_not_ready = True
                    time.sleep(1)
                    continue
        logging.info("all dm devices are ready")
    
    def link(self, device_id, device_method_name, value_name):
        link_obj = {
            "device_id": device_id,
            "device_method_name": device_method_name,
        }
        if value_name not in self.event_links:
            self.event_links[value_name] = []
        self.event_links[value_name].append(link_obj)
        logging.info("Device %s::%s linked with event value %s", device_id, device_method_name, value_name)
    
    def batch_update(self, event):
        for name, value in event.iteritems():
            for _, linked_events in self.event_links.iteritems():
                for linked_event in linked_events:
                    ch = self.get(linked_event.device_id).ch
                    getattr(ch, linked_event["device_method_name"])(value)
    def get_event(self):
        event = {}
        for id, device in self.device_repo.iteritems():
            event.update(device.get_event())
        return event
    def get_state(self):
        state = {}
        for id, device in self.device_repo.iteritems():
            state.update(device.get_state())
        return state
