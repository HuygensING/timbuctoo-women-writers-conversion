FROM ubuntu:22.04

RUN apt-get update &&\
    apt-get -y install vim

RUN apt-get -y install python-is-python3

# ENDPOINT tail -f /dev/null 
