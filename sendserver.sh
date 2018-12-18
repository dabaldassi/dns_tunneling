#!/bin/bash

scp -P 8081 src/serveur.py root@celforyon.fr:~/dns_tunneling
ssh -p 8081 root@celforyon.fr
echo coucou >> truc.txt
exit
