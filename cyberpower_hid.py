import hid

class CyberPower_HID:
    def __init__(self, device):
        self.device = device

    def close(self):
        if self.device is not None:
            self.device.close()
            self.device = None

    def __del__(self):
        self.close()

    def update(self):
        data = self.device.get_feature_report(0x13, 8)
        load = data[1] / 100
        data = self.device.get_feature_report(0x12, 8)
        vout = data[1]
        data = self.device.get_feature_report(0x0f, 8)
        vin = data[1]
        data = self.device.get_feature_report(0x08, 8)
        runtime = ((data[3] << 8) + data[2])
        battery = data[1] / 100
        data = self.device.get_feature_report(0x18, 8)
        capacity = (data[2] << 8) + data[1]
        load_w = load * capacity
        return load, load_w, vout, vin, runtime, battery, capacity

    @classmethod
    def open(cls, vid=0x0764, pid=0x0601):
        return CyberPower_HID(hid.Device(vid, pid))