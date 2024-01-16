FROM ubuntu:22.04

RUN RUN apt-get update &&\
    apt-get -y install vi
    apt-get -y install python3

ENDPOINT tail -f /dev/null 
