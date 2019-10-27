# DNS TUNELING

The purpose of this project is to send arbitrary data via DNS requests. It means setting  a client and a server process to exchange data with the DNS protocol. The server process partially implements a DNS server who knows how to decode our tampered requests and how to answer depending on it. The client has to create the right DNS queries with the data we want to send.

The development is made with the Python programming language and on the Linux operating system (with Debian).

We have made two main features using our DNS tunneling program: a distant shell and the encapsulation of the IP protocols in the DNS protocol. With the IP protocols wrapped, we can redirect any higher level protocol wrapped in them.

To use the programm you need to have your own domain name and replace devtoplay.com by yours in the sources.

## DNSSH

This feature allow to take control of a server and executes shell commands by using the DNS protocol.

### Client side

Add the ip adress of your router in the main function.

```bash

./client.py

```

### Server side

```bash

./server.py

```

## IP encapsulation

Encapsulate the IP protocol in the DNS protocol.

Socat is needed for this one to create a virtual network.

In the following example, 192.168.18.0 is a virtual network and 192.168.18.2 is the IP adress of the client in the virtual network and 192.168.18.1 is the server one.

### Client side

```bash

socat TUN:192.168.18.2/24,up EXEC:./clientStream.py

ip route add default via 192.168.18.1

```

### Server side

```bash

echo 1 > /proc/sys/net/ipv4/ip_forward

iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

socat TUN:192.168.18.1/24,up EXEC:./serveurStream.py

```

## Author

[alpapin](https://github.com/alpapin)

[dabaldassi](https://github.com/dabaldassi/)