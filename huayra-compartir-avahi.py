from six.moves import input
from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf
import requests

API_PORT = 9919
USE_API = True
API_URL_PREFIX = "http://localhost:9919"

import logging
import socket
import sys
import requests
import uuid
import netifaces

def get_ip_addr():
    EXCLUDE_IFACES = ['lo','lo0']
    ip_addr = "127.0.0.1"
    ifaces = filter(lambda i: i not in EXCLUDE_IFACES, netifaces.interfaces())

    for iface in ifaces:
        if netifaces.AF_INET in netifaces.ifaddresses(iface):
            ip_addr = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']

    return ip_addr


class MyListener(object):

    def remove_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if 'huayra-compartir-web-2' in name:
            machine_id = name.split("__")[1]
            print("- baja de servicio ", machine_id)

            if USE_API:
                requests.delete(API_URL_PREFIX + "/equipos/" + machine_id)

    def add_service(self, zeroconf, type, name):
        if 'huayra-compartir-web-2' in name:
            info = zeroconf.get_service_info(type, name)
            machine_id = name.split("__")[1]
            ip = '.'.join(str(ord(i)) for i in info.address)
            print("+ nuevo servicio ", ip, machine_id)

            if USE_API:
                data = {"host": ip, "id": machine_id}
                requests.post(API_URL_PREFIX + "/equipos", data)


# TODO: Obtener este numero desde machine-id
id = uuid.uuid1()

zeroconf = Zeroconf()
desc = {}
name = "huayra-compartir-web-2__" + str(id) + "__._http._tcp.local."
info = ServiceInfo("_http._tcp.local.", name, socket.inet_aton(get_ip_addr()), API_PORT, 0, 0, desc)

print("Anunciando servicio como: " + name)
zeroconf.register_service(info)


listener = MyListener()
browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)

try:
    input("Pulsa ENTER para salir...\n\n")
finally:
    zeroconf.unregister_service(info)
    zeroconf.close()
