#!/usr/bin/python

import binascii
import socket
from message import *


def send_udp_message(message, address, port):
    """send_udp_message sends a message to UDP server

    message should be a hexadecimal encoded string
    """
    server_address = (address, port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        #sock.sendto(binascii.unhexlify(message), server_address)
        print(message)
        sock.sendto(message, server_address)
        data, _ = sock.recvfrom(4096)
    finally:
        sock.close()
    return binascii.hexlify(data).decode("utf-8")


def format_hex(hex):
    """format_hex returns a pretty version of a hex string"""
    octets = [hex[i:i+2] for i in range(0, len(hex), 2)]
    pairs = [" ".join(octets[i:i+2]) for i in range(0, len(octets), 2)]
    return "\n".join(pairs)


message = "AA AA 01 00 00 01 00 00 00 00 00 00 " \
"06 67 6f 6f 67 6c 65 03 63 6f 6d 00 00 01 00 01"
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

header = Header("aaaa", 0, 0, False, False, True, False, 0, 0, 1, 0, 0, 0)
print(header)
question = Question("google.com")
print(question)
message = header.getMessage() + question.getMessage()

response = send_udp_message(message, "8.8.8.8", 53)
print(format_hex(response))
