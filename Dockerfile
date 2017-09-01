# fredhutch/scicomp-dashboard

FROM ubuntu:16.04

RUN apt-get -y update

RUN apt-get -y install python3 python3-pip curl vim

WORKDIR /


ADD . /scicomp-dashboard

WORKDIR /scicomp-dashboard


RUN pip3 install -r requirements.txt

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV FLASK_APP=app.py
# REMOVE THIS LINE vvv before a real deployment
ENV FLASK_DEBUG=True

# TODO deploy with gunicorn
CMD flask run -h 0.0.0.0
