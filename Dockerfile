# fredhutch/scicomp-dashboard

FROM ubuntu:16.04

ARG SLURMDASHBOARD_RSA

RUN apt-get -y update

RUN apt-get -y install python3 python3-pip curl vim

WORKDIR /


ADD . /scicomp-dashboard

WORKDIR /scicomp-dashboard

RUN echo $SLURMDASHBOARD_RSA | tr '~' '\n' > slurmdashboard_rsa && chmod 0400 slurmdashboard_rsa

RUN pip3 install pipenv

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN pipenv install --system

EXPOSE 8000

CMD ./run.sh
