#!/usr/bin/env python3

import os, configparser,argparse

INIFILE = "{0}/tradfri.ini".format(os.path.dirname(os.path.realpath(__file__)))

config = configparser.ConfigParser()

def SaveConfig(args):

    if os.path.exists(INIFILE):
        config.read(INIFILE)
    else: 
        config["Gateway"] = {"ip": "UNDEF", "key": "UNDEF"}

    if args.gateway != None:
        config["Gateway"]["ip"] = args.gateway

    if args.key != None:
        config["Gateway"]["key"] = args.key
    
    with open(INIFILE, "w") as configfile:
        config.write(configfile)

parser = argparse.ArgumentParser()
parser.add_argument("--gateway")
parser.add_argument("--key")

args = parser.parse_args()
SaveConfig(args)

with open(INIFILE, 'r') as fin:
    print (fin.read())