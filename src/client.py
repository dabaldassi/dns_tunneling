#!/usr/bin/python3
import signal
import socket
import time
from message import *


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
        while not("devtoplay.com" in message.qList[0].qname) or len(message.getAnswer()) == 0:
            data, _ = sock.recvfrom(4096)
            message = bytesToMessage(data)
        #print(message)
    finally:
        return message.getAnswer()[0].rdata


def main(inet="127.0.0.1"):
    global interruption
    signal.signal(signal.SIGINT, sigint_handler)
    header = Header("aaaa", 0, 0, False, False, True, False, 0, 0, 1, 0, 0, 0)
    question = Question("2woo.devtoplay.com")
    message = Message(header, [question])
    server_address = (inet, 53)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if(inet != "127.0.0.1"):
        s = ""
        c = 0
        t0 = 0
        while(s != 'exit'):
            if t0 != 0:
                print(time.time() - t0)
            print("root@dnsproject$ ", end="")
            s = input()
            s = s.replace('.', '\x07')
            t0 = time.time()
            if(s != 'exit') :
                question = Question(str(c)+s+".devtoplay.com")
                message = Message(header, [question])
                rdata = send_udp_message(message, sock, server_address)
                c += 1
                output = str(rdata, 'utf-8')
                while not interruption and rdata != b'\x00\x00\x00\x00':
                    question = Question(str(c) + s + ".devtoplay.com")
                    message = Message(header, [question])
                    rdata = send_udp_message(message, sock, server_address)
                    c += 1
                    output += str(rdata, 'utf-8')
                    if len(output) > 2048:
                        print(output, end='', flush=True)
                        output = ""
                print(output)
                if interruption:
                    interruption = False
                    question = Question(str(c) + "SIGINT" + ".devtoplay.com")
                    message = Message(header, [question])
                    send_udp_message(message, sock, server_address)
                    c += 1
    else:
        print("Argument error, socket bind on 127.0.0.1")
        send_udp_message(message.getBytes(), sock, server_address)


if __name__ == "__main__":
    main("192.168.99.1")


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
