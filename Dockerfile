FROM debian:latest

RUN apt-get update -y && \
  apt-get install -y python3 python3-pip git autoconf automake libtool && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* build/

RUN mkdir -p /usr/src/app /usr/src/build

RUN python3 -m pip install cython 

WORKDIR /usr/src/build
RUN git clone --depth 1 https://git.fslab.de/jkonra2m/tinydtls.git
WORKDIR /usr/src/build/tinydtls
RUN autoreconf
RUN ./configure --with-ecc --without-debug
WORKDIR /usr/src/build/tinydtls/cython
RUN python3 setup.py install

WORKDIR /usr/src/build
RUN git clone --depth 1 https://github.com/chrysn/aiocoap
WORKDIR /usr/src/build/aiocoap
RUN git reset --hard 3286f48f0b949901c8b5c04c0719dc54ab63d431
RUN python3 -m pip install --upgrade pip setuptools
RUN python3 -m pip install .

WORKDIR /usr/src/build
RUN git clone https://github.com/ggravlingen/pytradfri.git
WORKDIR /usr/src/build/pytradfri
RUN python3 setup.py install

WORKDIR /usr/src/app

# Default CoAP port
EXPOSE 5683

# CoAP port to increase header compression efficiency in 6LoWPANs
EXPOSE 61616  

# Adaptor port 
EXPOSE 1234

CMD bash
