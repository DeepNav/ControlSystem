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
        self.ch_event_listernings = {}

    def is_ready(self):
        return (self.is_attached and self.is_stable)

    def get_event(self):
        e = self.event
        self.event = {}
        return e

    def get_state(self):
        return self.state

    def set_event_val(self, key, val):
        if (key in self.state and val != self.state[key]) or key not in self.state:
            if val is not None:
                self.event[key] = val
                self.state[key] = val

    def on_attach(self):
        pass

    def listen(self, event_name, callback_fn):
        getattr(self.ch, "setOn" + event_name + "Handler")(callback_fn)
        self.ch_event_listernings[event_name] = callback_fn

    def unlisten(self, event_name):
        getattr(self.ch, "setOn" + event_name + "Handler")(None)

    def unlisten_all(self):
        for event_name, callback_fn in self.ch_event_listernings.iteritems():
            self.unlisten(event_name)

    def restore_listerners(self):
        for event_name, callback_fn in self.ch_event_listernings.iteritems():
            self.listen(event_name, callback_fn)


class Device_Manager(object):
    def __init__(self):
        self.device_repo = {}
        self.event_links = {}

    def __device_detached(self, device):
        logging.warn("Device detached: %s", device.device_id)
        device.unlisten_all()
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
            
        self.device_repo[device.device_id] = device
        device.ch.setOnAttachHandler(onAttached)
        device.ch.setOnDetachHandler(onDetached)
        device.ch.setOnErrorHandler(onError)
        device.ch.open()
        

    def waitUntilAllReady(self):
        logging.info("Start to wait for all devices to become ready")
        someone_not_ready = True
        while someone_not_ready:
            someone_not_ready = False
            for id, device in self.device_repo.iteritems():
                if not device.is_ready():
                    logging.info(
                        "some device is not ready, keep waiting: %s", device.device_id)
                    someone_not_ready = True
                    time.sleep(1)
                    continue
        logging.info("all dm devices are ready")

    def link(self, device_id, device_method_name, value_name, value_translator=lambda val: val):
        link_obj = {
            "device_id": device_id,
            "device_method_name": device_method_name,
            "value_translator": value_translator,
        }
        if value_name not in self.event_links:
            self.event_links[value_name] = []
        self.event_links[value_name].append(link_obj)
        logging.info("Device %s::%s linked with event value %s",
                     device_id, device_method_name, value_name)

    def batch_update(self, event):
        for name, value in event.iteritems():
            if name in self.event_links:
                for linked_event in self.event_links[name]:
                    device = self.get(linked_event["device_id"])
                    if device.is_ready():
                        ch = self.get(linked_event["device_id"]).ch
                        getattr(ch, linked_event["device_method_name"])(
                            linked_event["value_translator"](value))
                    else:
                        logging.warning(
                            "%s is not ready when dispatching event", device.device_id)

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
