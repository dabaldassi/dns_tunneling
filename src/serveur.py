#!/usr/bin/python3

import socket
from message import *

serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

serversocket.bind(("10.0.2.15", 53))

while True:
    data, ad = serversocket.recvfrom(4096)
    print(data)
    q = bytesToMessage(data)
    print(q)
    message = Message(Header(q.header.id, 1, 0, False, False, True, True, 0, 0, 1, 1, 0, 0), q.qList, [RR("google.com", b'\x01\x01\x01\x01', 1, 1, 1172)])
    print(message)
    print(message.getBytes())
    serversocket.sendto(message.getBytes(), ad)
