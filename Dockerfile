FROM ubuntu:20.04

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python3-pip
COPY ./requirements.txt /root/requirements.txt
COPY ./export_ups.py /root/export_ups.py

WORKDIR /root
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "/root/export_ups.py"]

