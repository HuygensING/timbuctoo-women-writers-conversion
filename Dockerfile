FROM ubuntu:22.04

RUN apt-get update &&\
    apt-get -y install vim

RUN apt-get -y install python-is-python3

RUN apt-get -y install pip

RUN pip install requests

ENTRYPOINT ["tail", "-f", "/dev/null"]

