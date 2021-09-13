# Prometheus exporter for Rack UPS (Cyperpower)

## Requirements
- python3

## Running via Docker
The provided Dockerfile will build a suitable container for running the exporter.
1. Build the container via `docker build -t cyper_exporter:latest .`
2. Running the container you must specify port, usb-device, and baud rates
```
docker run --device=<USB device> -p <port:port> -t cyber_exporter:latest -p <port> -d <device> -b <baud>
```

If you have your prometheus server running on another container on this machine, you can also specify the network so that it can be scraped. For example:

```
docker run --name=cyber_monitor --restart always -d --device=/dev/ttyUSB0 -p 9825:9825 --network=ec-prom-graf_monitor-net -t cyber_exporter:latest -p 9825 -d /dev/ttyUSB0 -b 2400
```

## Installing via the install.sh script
You can use the provided install.sh script to generate and start a service (ups-exporter.serice) for monitoring

