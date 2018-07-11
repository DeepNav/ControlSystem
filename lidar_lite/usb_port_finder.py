from serial.tools.list_ports import comports


def find_port_for(device_name):
    ports = list(comports())
    for p in ports:
        if device_name in p.description:
            return p.device
    return None


def find_arduino_port():
    return find_port_for("Generic CDC")


def wait_until_arduino_connected():
    device = None
    while device is None:
        device = find_arduino_port()
    return device
