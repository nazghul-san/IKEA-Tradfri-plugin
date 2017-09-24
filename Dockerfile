FROM debian:latest

RUN apt-get update -y && \
  apt-get install -y python3 python3-pip git autoconf automake libtool && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* build/

RUN mkdir -p /usr/src/app /usr/src/build

RUN python3 -m pip install cython 
RUN python3 -m pip install ipython 
RUN python3 -m pip install --upgrade "git+https://github.com/chrysn/aiocoap#egg=aiocoap[all]"
RUN python3 -m pip install pytradfri

WORKDIR /usr/src/app

# Default CoAP port
EXPOSE 5683

# CoAP port to increase header compression efficiency in 6LoWPANs
EXPOSE 61616  

# Adaptor port 
EXPOSE 1234

CMD bash
