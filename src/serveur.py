#!/usr/bin/python3

import sys
import socket
from message import *


def calculator(op):
    print(op, op[0])
    r = 0
    
    if(op[0] == int("ad", 16)):
        r  = op[1] + op[2]
    
    return r.to_bytes(1,'big')

serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if(len(sys.argv) == 2):
    serversocket.bind((sys.argv[1], 53))
else:
    print("Argument error, socket bind on 127.0.0.1")
    serversocket.bind(("127.0.0.1",53))

while True:
    data, ad = serversocket.recvfrom(4096)
    print(data)
    q = bytesToMessage(data)
    print(q)
    print(q.rrList[0].rdata)

    # res = calculator(q.rrList[0].rdata)
    res = b'\x01\x01\x01\x01'
    
    cmd = q.qList[0].qname.split(".")

    if(cmd[0] == "woo"):
        res = b'\x02\x02\x02\x02\x01\xAA\x12'
        
    
    message = Message(Header(q.header.id, 1, 0, False, False, True, True, 0, 0, 1, 0, 0, 1), q.qList, [RR(q.qList[0].qname,res, 16, 1, 1)])

    print(message)
    print(message.getBytes())
    serversocket.sendto(message.getBytes(), ad)
