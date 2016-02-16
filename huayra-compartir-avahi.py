#!/usr/bin/env python

import sys
import time
import signal
import socket
import argparse
import requests
import netifaces
from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf


API_PORT = 9919
USE_API = True
API_URL_PREFIX = "http://localhost:{}".format(API_PORT)
IS_RUNNING = False
VERBOSE = False


class CompartirListener(object):
    def __init__(self, verbose=False, *args, **kwargs):
        self.verbose = verbose

    def remove_service(self, zeroconf, type, name):
        #info = zeroconf.get_service_info(type, name)
        if 'huayra-compartir-web-2' in name:
            machine_id = name.split("__")[1]
            if self.verbose:
                print("- baja de servicio ", machine_id)

            if USE_API:
                requests.delete(API_URL_PREFIX + "/equipos/" + machine_id)


    def add_service(self, zeroconf, type, name):
        if 'huayra-compartir-web-2' in name:
            info = zeroconf.get_service_info(type, name)
            machine_id = name.split("__")[1]
            ip = '.'.join(str(ord(i)) for i in info.address)
            if self.verbose:
                print("+ nuevo servicio ", ip, machine_id)

            if USE_API:
                data = {"host": ip, "id": machine_id}
                requests.post(API_URL_PREFIX + "/equipos", data)


def get_ip_n_macaddr():
    EXCLUDE_IFACES = ['lo', 'lo0']
    ip_addr = "127.0.0.1"
    mac_addr = "ff:ff:ff:ff:ff:ff"
    ifaces = filter(lambda i: i not in EXCLUDE_IFACES, netifaces.interfaces())

    for iface in ifaces:
        if netifaces.AF_INET in netifaces.ifaddresses(iface):
            ip_addr = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
            mac_addr = netifaces.ifaddresses(iface)[netifaces.AF_PACKET][0]['addr']

    return (ip_addr, mac_addr)


def register(zeroconf, info):
    """
    Registra un servicio avahi
    """
    global IS_RUNNING, VERBOSE
    if VERBOSE:
        print("Anunciando servicio como: " + info.name)
    zeroconf.register_service(info)
    IS_RUNNING = True


def unregister(zeroconf, info):
    """
    Desregistra(?) un servicio avahi
    """
    global browser
    zeroconf.unregister_service(info)
    zeroconf.close()

    browser.cancel()


def signal_handler(sig, frame):
    global zeroconf, info, IS_RUNNING

    unregister(zeroconf, info)
    IS_RUNNING = False

    time.sleep(5)
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose',
                        action="store_true",
                        help="Prints status messages")

    args = parser.parse_args()
    VERBOSE = args.verbose

    ip, mac = get_ip_n_macaddr()
    zeroconf = Zeroconf()
    desc = {}
    name = "huayra-compartir-web-2__" + str(mac) + "__._http._tcp.local."
    info = ServiceInfo("_http._tcp.local.", name, socket.inet_aton(ip), API_PORT, 0, 0, desc)

    listener = CompartirListener(args.verbose)
    browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)

    register(zeroconf, info)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        raw_input("<ENTER> para salir" if VERBOSE else "")
    finally:
        if IS_RUNNING:
            unregister(zeroconf, info)
