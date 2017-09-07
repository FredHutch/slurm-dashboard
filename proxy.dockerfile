# dockerimages.fhcrc.org/fredhutch/scicomp-dashboard-certs
FROM ubuntu:16.04
# FROM jwilder/nginx-proxy

RUN apt-get -y update && apt-get install -y curl

RUN mkdir /certs

RUN curl -L http://dist.fhcrc.org/wildcard2014/2b497ffb67edc8.crt > /certs/scicomp-dashboard.fhcrc.org.crt
RUN ls -l /certs
RUN curl -L http://dist.fhcrc.org/wildcard2014/fhcrc.org.key > /certs/scicomp-dashboard.fhcrc.org.key && chmod 0400 /certs/scicomp-dashboard.fhcrc.org.key

RUN ls -l /certs
