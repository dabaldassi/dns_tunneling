#!/usr/bin/python

import socket
import binascii
from message import *

serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

serversocket.bind(("10.0.2.15", 53))

#serversocket.listen(5)

while True:
    #(clientsocket, address) = serversocket.accept()
    data, ad = serversocket.recvfrom(4096)
    print(data)
    print()
    data = binascii.hexlify(data).decode("utf-8")
    print(data)
    #print(data[0:4].replace(" ", "")+"8180000100010000000006676f6f676c6503636f6d0000010001c00c0001000100000494000401010101")
    serversocket.sendto(binascii.unhexlify(data[0:4].replace(" ", "")+"8180000100010000000006676f6f676c6503636f6d0000010001c00c0001000100000494000401010101"), ad)
