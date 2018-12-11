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
    q = bytesToMessage(data)
    data = binascii.hexlify(data).decode("utf-8")
    #print(data[0:4].replace(" ", "")+"8180000100010000000006676f6f676c6503636f6d0000010001c00c0001000100000494000401010101")
    message = Message(Header("aaaa", 1, 0, False, False, True, True, 0, 0, 1, 1, 0, 0), q.qList, [RR("google.com", b'\x01\x01\x01\x01', 1, 1, 1172)])
    print(message)
    print(message.getBytes())
    serversocket.sendto(message.getBytes(), ad)

    #serversocket.sendto(binascii.unhexlify(data[0:4].replace(" ", "")+"8180000100010000000006676f6f676c6503636f6d0000010001c00c0001000100000494000401010101"), ad)
