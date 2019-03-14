#!/usr/bin/python3

from threading import Thread
import sys
import os
import signal
import socket
import time
from message import *
from stream import *
import time

interruption = False

def sigint_handler(signum, frame):
    global interruption
    interruption = True


def send_udp_message(message, sock, server_address):
    """send_udp_message sends a message to UDP server

    message should be a hexadecimal encoded string
    """
    try:
        sock.sendto(message.getBytes(), server_address)
        data, _ = sock.recvfrom(4096)
        message = bytesToMessage(data)
        while not("devtoplay.com" in message.qList[0].qname):
            data, _ = sock.recvfrom(4096)
            message = bytesToMessage(data)
        #print(message)
    finally:
        return message


def main(inet="127.0.0.1"):
    server_address = (inet, 53)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    global interruption
    signal.signal(signal.SIGINT, sigint_handler)

    header = Header('aaaa', 0, 0)

    command = ''
    salt = 0

    while command != 'exit':
        print("root@dnsproject$", end=" ")
        command = input()
        t0 = time.time()
        command = command.replace('.', '\x07')

        if command != 'exit':
            question = Question(str(salt)+command+".devtoplay.com", 16)
            message = Message(header, [question])

            receipt = send_udp_message(message, sock, server_address)
            salt += 1

            output = ''
            txt_length = -1

            if len(receipt.getAnswer()) > 0:
                i = 0
                while len(receipt.getAnswer()[0].rdata[i:]) > 0:
                    txt_length = receipt.getAnswer()[0].rdata[i]
                    i += 1
                    output += str(receipt.getAnswer()[0].rdata[i:i+txt_length], 'utf-8')
                    i += txt_length

            while not interruption and receipt.header.rcode == 0 and txt_length != 0:
                if len(output) > 2048:
                    print(output, end='', flush=True)
                    output = ''

                question = Question(str(salt)+command+".devtoplay.com", 16)
                message = Message(header, [question])

                receipt = send_udp_message(message, sock, server_address)
                salt += 1

                txt_length = -1

                if len(receipt.getAnswer()) > 0:
                    i = 0
                    while len(receipt.getAnswer()[0].rdata[i:]) > 0:
                        txt_length = receipt.getAnswer()[0].rdata[i]
                        i += 1
                        output += str(receipt.getAnswer()[0].rdata[i:i + txt_length], 'utf-8')
                        i += txt_length

            print(output)
            print(time.time()-t0)

            if interruption:
                interruption = False
                question = Question(str(salt) + "SIGINT.devtoplay.com", 16)
                message = Message(header, [question])
                send_udp_message(message, sock, server_address)
                salt += 1

def next_salt(salt):
    mask_salt = 0xffffffff
    nb_bytes_salt = mask_salt.bit_length() >> 3

    while(True):
        salt[0] = (salt[0] + 1) & mask_salt
        saltstring = str(salt[0].to_bytes(nb_bytes_salt,'big'),'latin-1')

        if(not '.' in saltstring):
            break

    return saltstring

def dataToLabel(data):
    size = 62
    result = ''

    data = str(data,'latin-1')

    for i in range(0,len(data),size):
        result += removePoint(data[i:i+size])
        result += '.'

    return result

def mainStream(inet="127.0.0.1"):
    s = Stream()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (inet,53)
    header = Header('aaaa', 0, 0)
    salt = [0]
    qtype = 16
    size = 222
    
    while(True):
        data = s.read()
        #data_split = [ data[i:i+size] for i in range(0,len(data),size) ]

        for i in range(0,len(data),size):
            question = [Question(next_salt(salt)+'.'+dataToLabel(data[i:i+size])+'devtoplay.com',qtype)]
            message = Message(header,question)
            receipt = send_udp_message(message,sock,server_address)

        receiving = True
        data_received = b''
        while(receiving):
            message = Message(header, [Question(next_salt(salt)+"you.devtoplay.com", qtype)])
            receipt = send_udp_message(message,sock,server_address)
        
            for answer in receipt.getAnswer():
                if(answer.type_data == qtype):
                    data = readTXT(answer.rdata)
                    if(data != b'nothing'):
                        data_received += data
                    else:
                        receiving = False
        
        if(data_received != b''):
            sys.stdout.buffer.write(data_received)
            sys.stdout.flush()

if __name__ == "__main__":
    #main()
    mainStream("91.121.145.188") # Celforyon
    #mainStream("192.168.0.12") # Brutal PC
   # mainStream("192.168.0.254") # Ma box
    #mainStream("172.27.141.254") # Eduspot
    #mainStream("192.168.99.1") # Muscibot
    #mainStream("192.168.43.1") # CAFEBABE

    
### Header ###
# AA AA == ID(16)
# 01 == Qr(1), Opcode(4), Aa(1), Tc(1), Rd(1)
# 00 == Ra(1), Z(3), Rcode(4)
# 00 01 == Qdcount(16)
# 00 00 = Ancount(16)
# 00 00 == Nscount(16)
# 00 00 == Arcount(16)
### Question ###
# 06 67 6f 6f 67 6c 65 03 63 6f 6d 00 == Qname
    # 06 == Qname length (6 octets for "google")
    # 67 6f 6f 67 6c 65 == "google"
    # 03 63 6f 6d == "com" length + "com"
    # 00 == Qname end
# 00 01 == Qtype(16)
# 00 01 == Qclass(16)
### Answer ###
# C0 0C == Name(11 .. .. .. .. .. ..) points first occurence of the domain name
# 00 01 == Type(16)
# 00 01 == Class(16)
# 00 00 04 94 == TTL(32)
# 00 04 == Rdlength(16) 4 octets in this case
# 01 01 01 01 == Rdata
