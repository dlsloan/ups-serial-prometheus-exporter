import argparse
import signal
import serial
import time

from prometheus_client import start_http_server, Gauge, Enum, Info

IN_VOLTS = Gauge('ups_in_volts', 'Current UPS input voltage')
OUT_VOLTS = Gauge('ups_out_volts', 'Current UPS output voltage')
LOAD = Gauge('ups_load_percentage', 'Current UPS load percentage')
LOAD_W = Gauge('ups_load_w', 'Current UPS load wattage')
BATTERY = Gauge('ups_battery_percentage', 'Current UPS battery percentage')
FREQUENCY = Gauge('ups_freq', 'Current UPS ac frequency')
BATTERY_RUNTIME = Gauge('ups_battery_runtime', 'Available UPS battery runtime seconds')
RATED_VA = Gauge('ups_rated_va', 'UPS rated VA')
RATED_W = Gauge('ups_rated_w', 'UPS rated W')
NOM_V = Gauge('ups_nom_v', 'UPS nominal voltage')
MIN_FRQ = Gauge('ups_min_frq', 'Minimum UPS input frequency')
MAX_FRQ = Gauge('ups_max_frq', 'Maximum UPS input frequency')

def parse_args():
    parser = argparse.ArgumentParser(description="Prometheus exporter for rack UPS")
    parser.add_argument('-p', '--port', default=9825, help='Port to listen on for the exporter')
    parser.add_argument('-v', '--verbose', default=0, action='count')
    return parser.parse_args()


def run_cmd(cmd):
    port.write(cmd + b'\r')
    ret = b''
    while not len(ret) or ret[-1:] != b'\r':
        ret += port.read(1)
    return ret

def get_raw_state():
    data = run_cmd(b'D')
    in_volts = float(data[2:7])
    out_volts = float(data[8:13])
    load = float(data[14:17]) / 100
    battery = float(data[18:21]) / 100
    frequency = float(data[32:37])
    run_time = float(data[38:41]) * 60
    return in_volts, out_volts, load, battery, frequency, run_time

def get_limits():
    data = run_cmd(b'P2')[1:].strip().split(b',')
    max_va = int(data[0])
    max_w = int(data[1])
    nom_v = int(data[2])
    min_frq = int(data[3])
    max_frq = int(data[4])
    return max_va, max_w, nom_v, min_frq, max_frq

def update_state():
    in_volts, out_volts, load, battery, frequency, run_time = get_raw_state()
    max_va, max_w, nom_v, min_frq, max_frq = get_limits()
    if args.verbose > 0:
        print('state: ', in_volts, out_volts, load, battery, frequency, run_time)
        print('limits: ', max_va, max_w, nom_v, min_frq, max_frq)
    IN_VOLTS.set(in_volts)
    OUT_VOLTS.set(out_volts)
    LOAD.set(load)
    LOAD_W.set(load * max_w)
    BATTERY.set(battery)
    FREQUENCY.set(frequency)
    BATTERY_RUNTIME.set(run_time)
    RATED_VA.set(max_va)
    RATED_W.set(max_w)
    NOM_V.set(nom_v)
    MIN_FRQ.set(min_frq)
    MAX_FRQ.set(max_frq)

running = True

def stop_handler(sig, frame):
    global running

    running = False
    print('stopping...')

if __name__ == '__main__':
    port = serial.Serial('/dev/ttyUSB0', baudrate=2400)
    args = parse_args()
    start_http_server(args.port)
    signal.signal(signal.SIGINT, stop_handler)
    while running:
        update_state()
        time.sleep(5)

