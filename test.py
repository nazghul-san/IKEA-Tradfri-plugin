#!/usr/bin/env python3
import asyncio
import json
import configparser, os

INIFILE = "{0}/tradfri.ini".format(os.path.dirname(os.path.realpath(__file__)))

config = configparser.ConfigParser()

if os.path.exists(INIFILE):
    config.read(INIFILE)
else: 
    config["Gateway"] = {"ip": "UNDEF", "key": "UNDEF"}

class EchoClientProtocol(asyncio.Protocol):
    transport = None

    def __init__(self, message, loop):
        self.message = message
        self.loop = loop

    def connection_made(self, transport):
        # transport.write(self.message.encode())
        #print('Data sent: {!r}'.format(self.message))
        self.transport = transport
        pass

    def data_received(self, data):
        print('Data received: {!r}'.format(data.decode()))

        decoded = data.decode("utf-8")
        decoded = '[' + decoded.replace('}{', '},{') + ']'
        commands = json.loads(decoded)

        for command in commands:
            if command['action']=="clientConnect":
                self.send_data({"action":"setConfig", "gateway": config["Gateway"]['ip'], "key": config["Gateway"]["key"], "observe": True})

            if command['action']=="setConfig":
                self.send_data({"action":"getLights"})

            if command['action']=="getLights":
                self.send_data({'action': 'setState', 'state': 'Off', 'deviceID': '65537'})


    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event loop')
        self.loop.stop()

    def send_data(self, dict):
        self.transport.write(json.dumps(dict).encode(encoding='utf_8'))
        print('Data sent: {!r}'.format(dict))

loop = asyncio.get_event_loop()
message = 'Hello World!'
coro = loop.create_connection(lambda: EchoClientProtocol(message, loop),
                              '127.0.0.1', 1234)
loop.run_until_complete(coro)
loop.run_forever()
loop.close()