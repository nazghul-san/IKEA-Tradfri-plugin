#!/usr/bin/env python3

import asyncio
import json, configparser, os

from pytradfri import Gateway
from pytradfri.api.aiocoap_api import api_factory

version = 0.1

try:
    # pylint: disable=ungrouped-imports
    from asyncio import ensure_future
except ImportError:
    # Python 3.4.3 and earlier has this as async
    # pylint: disable=unused-import
    from asyncio import async
    ensure_future = async

def stringToBool(boolString):
    if boolString == "True":
        return True
    elif boolString == "False":
        return False
    else:
        return None

# Device Configurations
INIFILE = "{0}/devices.ini".format(os.path.dirname(os.path.realpath(__file__)))
deviceDefaults = {"Dimmable": True, "HasWB": True, "HasRGB": False}

deviceConfig = configparser.ConfigParser()

if os.path.exists(INIFILE):
    deviceConfig.read(INIFILE)


loop = asyncio.get_event_loop()

class IkeaFactory():
    gateway = None
    api = None

    devices = None
    groups = None

    def __init__(self):
        pass

    async def initGateway(self, client, ip, key, observe):
        print("Setting gateway")
        self.api = await api_factory(ip, key)
        self.gateway = Gateway()

        client.send_data({"action":"setConfig", "status": "Ok"})

    async def getLights(self, client):
        resultDevices = []
        answer = {}
        configChanged = False

        self.devices = await self.api(*await self.api(self.gateway.get_devices()))
        self.groups = await self.api(*await self.api(self.gateway.get_groups()))

        lights = [dev for dev in self.devices if dev.has_light_control]        

        for aLight in lights:
            
            if not aLight.device_info.model_number in deviceConfig:
                print("Device settings not found for {0}. Creating defaults!".format(aLight.device_info.model_number))
                deviceConfig[aLight.device_info.model_number] = deviceDefaults
                configChanged = True
            
            resultDevices.append({"DeviceID": aLight.id, "Name": aLight.name, "Type": "Light", "Dimmable": stringToBool(deviceConfig[aLight.device_info.model_number]['dimmable']), "HasWB": stringToBool(deviceConfig[aLight.device_info.model_number]['haswb']), "HasRGB": stringToBool(deviceConfig[aLight.device_info.model_number]['hasrgb'])})

        for aGroup in self.groups:
            #print (aGroup)
            resultDevices.append({"DeviceID": aGroup.id, "Name": "Group - "+aGroup.name, "Type": "Group", "Dimmable": True, "HasWB": False})

        if configChanged:
            with open(INIFILE, "w") as configfile:
                deviceConfig.write(configfile)

        answer["action"] = "getLights"
        answer["status"] = "Ok"
        answer["result"] =  resultDevices

        client.send_data(answer)

    async def getStates(self, client):

        if self.devices is not None:
            lights = [dev for dev in self.devices if dev.has_light_control]
            for aLight in lights:
                print(aLight)


            

# an instance of EchoProtocol will be created for each client connection.
class IkeaProtocol(asyncio.Protocol):
    transport = None

    factory = IkeaFactory()

    def connection_made(self, transport):
        self.transport = transport
        print("Connected")

        self.send_data({"action": "clientConnect", "status": "Ok", "version": version})

    def data_received(self, data):
        # self.transport.write(data)
        print("Received: {0}".format(data))
        
        decoded = data.decode("utf-8")
        decoded = '[' + decoded.replace('}{', '},{') + ']'
        commands = json.loads(decoded)

        for command in commands:
            if command['action']=="setConfig":
                # print("Setting config")
                loop.create_task(self.factory.initGateway(self, command['gateway'], command['key'], command['observe']))

            if command['action']=="getLights":
                loop.create_task(self.factory.getLights(self))

            if command['action']=="getStates":
                loop.create_task(self.factory.getStates(self))

            # if command['action']=="getLights":
            #     self.factory.sendDeviceList(self)

            # if command['action']=="setLevel":
            #     self.factory.setLevel(self, command["deviceID"], command["level"])

            # if command['action']=="setState":
            #     self.factory.setState(self, command["deviceID"], command["state"])

            # if command['action']=="setWB":
            #     self.factory.setWB(self, command["deviceID"], command['hex'])

    def connection_lost(self, exc):
        self.transport.close()
        #server.close()
        print("Disconnected")

    def send_data(self, dict):
        self.transport.write(json.dumps(dict).encode(encoding='utf_8'))

loop = asyncio.get_event_loop()
# Each client connection will create a new protocol instance
coro = loop.create_server(IkeaProtocol, '', 1234)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('IKEA aiocoap-adapter version {0} listening on {1}'.format(version, server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()