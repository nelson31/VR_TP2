FROM ubuntu:20.04

RUN apt update
RUN apt -y install python3.7
RUN apt -y install python3-pip
RUN cd /usr/local/bin/httpserv/
RUN pip3 install -r requirements.txt
RUN python3 httpf.py


