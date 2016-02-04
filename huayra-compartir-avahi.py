from six.moves import input
from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf

API_PORT = 9919

import logging
import socket
import sys
import requests
import uuid


class MyListener(object):

    def remove_service(self, zeroconf, type, name):
        print("- Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        #print "1"
        #print("+ Service %s created" %(name,))
        #print "2"
        #print name
        #print "44"
        #print info.get_name()
        #print "66"
        ip = '.'.join(str(ord(i)) for i in info.address)
        print(ip + " como " + name)
        #print "3"
        #print name, info

# TODO: Obtener este numero desde machine-id
id = uuid.uuid1()

zeroconf = Zeroconf()
desc = {}
info = ServiceInfo("_http._tcp.local.", "huayra-compartir-web-2__" + str(id) + "__._http._tcp.local.",
                   socket.inet_aton("127.0.0.1"), API_PORT, 0, 0, desc)

print("Anunciando servicio")
zeroconf.register_service(info)


listener = MyListener()
browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)

try:
    input("Pulsa ENTER para salir...\n\n")
finally:
    zeroconf.unregister_service(info)
    zeroconf.close()
