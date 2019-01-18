#!/usr/bin/python3

import sys
import os
import socket
from message import *


def send_udp_message(message, address, port):
    """send_udp_message sends a message to UDP server

    message should be a hexadecimal encoded string
    """
    server_address = (address, port)
    print(message)
    print(bytesToMessage(message))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(message, server_address)
        data, _ = sock.recvfrom(4096)
        print(data)
        #print(bytesToMessage(data).rrList[0].rdata.decode())
        print(bytesToMessage(data))
        
    finally:
        sock.close()
    return

header = Header("aaaa", 0, 0, False, False, True, False, 0, 0, 1, 0, 0, 0)
question = Question("2woo.devtoplay.com")
#question = Question("google.com")

message = Message(header, [question])

#print(message)
#print(message.getBytes())

if(len(sys.argv) == 2):
    s = ""
    c = 0
    while(s != 'exit'):
        print("root@dnsproject$ " , end="")
        s = input()

        if(s != 'exit') :
            question = Question(str(c)+s+".devtoplay.com")
            #question = Question("foo.devtoplay.com")
            message = Message(header, [question])
            send_udp_message(message.getBytes(), sys.argv[1], 53)
            c += 1
else:
    print("Argument error, socket bind on 127.0.0.1")
    send_udp_message(message.getBytes(), "127.0.0.1", 53)

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
