# dockerimages.fhcrc.org/fredhutch/scicomp-dashboard-proxy
FROM jwilder/nginx-proxy

RUN apt-get -y update && apt-get install -y curl



RUN curl -L http://dist.fhcrc.org/wildcard2014/2b497ffb67edc8.crt > /etc/nginx/certs/scicomp-dashboard.fhcrc.org.crt
RUN curl -L http://dist.fhcrc.org/wildcard2014/fhcrc.org.key > /etc/nginx/certs/scicomp-dashboard.fhcrc.org.key
RUN chmod 0400 /etc/nginx/certs/scicomp-dashboard.fhcrc.org.key
