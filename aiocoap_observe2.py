#!/usr/bin/env python3

# This file is part of the Python aiocoap library project.
#
# Copyright (c) 2012-2014 Maciej Wasilak <http://sixpinetrees.blogspot.com/>,
#               2013-2014 Christian Amsüss <c.amsuess@energyharvesting.at>
#
# aiocoap is free software, this file is published under the MIT license as
# described in the accompanying LICENSE file.

"""This is a usage example of aiocoap that demonstrates how to implement a
simple client. See the "Usage Examples" section in the aiocoap documentation
for some more information."""

import configparser, os

import asyncio

from pytradfri import Gateway
from pytradfri.api.aiocoap_api import api_factory

INIFILE = "{0}/tradfri.ini".format(os.path.dirname(os.path.realpath(__file__)))

config = configparser.ConfigParser()

if os.path.exists(INIFILE):
    config.read(INIFILE)
else: 
    config["Gateway"] = {"ip": "UNDEF", "key": "UNDEF"}

observations = None

async def cleanupTasks():
    for task in asyncio.Task.all_tasks():
       task.cancel()

async def heartbeat(verbose=False):
    while 1:
        print("\nTasks: {0}".format(len(asyncio.Task.all_tasks())))
        
        if verbose:
            for task in asyncio.Task.all_tasks():
                print(task)
        
        await asyncio.sleep(2)

def observe_callback(updated_device):
    light = updated_device.light_control.lights[0]
    print("Received message for: %s" % light)

def observe_err_callback(err):
    print('observe error:', err)

async def run():
    reshedule_interval = 30

    observations = []

    api = await api_factory(config["Gateway"]["ip"], config["Gateway"]["key"])
    gateway = Gateway()
    
    devices_command = gateway.get_devices()
    devices_commands = await api(devices_command)
    devices = await api(*devices_commands)

    lights = [dev for dev in devices if dev.has_light_control]

    for light in lights:
        observe_command = light.observe(observe_callback, observe_err_callback,
                                        duration=reshedule_interval+1)
        #Start observation as a second task on the loop.
        observations.append(asyncio.ensure_future(api(observe_command)))
        # Yield to allow observing to start.
        await asyncio.sleep(0)

    await asyncio.sleep(reshedule_interval)
        
    while 1:
        for task in observations:
            task.cancel()
            asyncio.ensure_future(task)

        print("Resheduled")
        await asyncio.sleep(reshedule_interval)
    
    print("Finally done")



loop = asyncio.get_event_loop()

# Run until Ctrl+C is pressed
# task = asyncio.ensure_future(heartbeat())
task = asyncio.ensure_future(run())

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close
loop.run_until_complete(cleanupTasks())
loop.close()    
