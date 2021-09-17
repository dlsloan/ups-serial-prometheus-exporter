import argparse
import signal
import time
import traceback

from prometheus_client import start_http_server, Gauge, Enum, Info
from cyberpower_hid import CyberPower_HID

IN_VOLTS = Gauge('ups_in_volts', 'Current UPS input voltage')
OUT_VOLTS = Gauge('ups_out_volts', 'Current UPS output voltage')
LOAD = Gauge('ups_load_percentage', 'Current UPS load percentage')
LOAD_W = Gauge('ups_load_w', 'Current UPS load wattage')
BATTERY = Gauge('ups_battery_percentage', 'Current UPS battery percentage')
BATTERY_RUNTIME = Gauge('ups_battery_runtime', 'Available UPS battery runtime seconds')
RATED_W = Gauge('ups_rated_w', 'UPS rated W')

def parse_args():
    parser = argparse.ArgumentParser(description="Prometheus exporter for rack UPS")
    parser.add_argument('-p', '--port', type=int, default=9826, help='Port to listen on for the exporter')
    parser.add_argument('-d', '--device', type=str, default='/dev/ttyUSB0', help='Serial USB device to probe')
    parser.add_argument('-b', '--baud', type=int, default=2400, help='Baud rate for the serial USB device')
    parser.add_argument('-v', '--verbose', default=0, action='count')
    return parser.parse_args()

def update_state():
    try:
        load, load_w, vout, vin, runtime, battery, capacity = dev.update()
        IN_VOLTS.set(vin)
        OUT_VOLTS.set(vout)
        LOAD.set(load)
        LOAD_W.set(load_w)
        BATTERY.set(battery)
        BATTERY_RUNTIME.set(runtime)
        RATED_W.set(capacity)
        if args.verbose > 0:
            print(f'load: {load}({load_w} W), in: {vin} V, out: {vout} V, battery: {battery} ({runtime} s), maximum capacity: {capacity} W')
    except Exception as e:
        traceback.print_exc()
        print(str(e))

running = True

def stop_handler(sig, frame):
    global running

    running = False
    print('stopping...')

if __name__ == '__main__':
    args = parse_args()
    start_http_server(args.port)
    signal.signal(signal.SIGINT, stop_handler)
    dev = CyberPower_HID.open()
    try:
        while running:
            update_state()
            time.sleep(5)
    finally:
        dev.close()
