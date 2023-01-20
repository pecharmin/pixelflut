#!/usr/bin/env python3
#coding: utf8

# TODO
# * Snake im Rahmen halten
# * Farben ausscheiden (Array analog zu snake[])

# PX <hor> <ver>

import socket
from time import sleep

p = ('192.168.11.171', 1234)
h = 1280
w = 1920

snake = []
for i in range(int(w/2), int(w/2)+75):
    snake.append([i, int(h/2)])
c = 'ffffff'
# d:
# 0: oben - y+1
# 1: rechts - x+1
# 2: unten - y-1
# 3: links - x-1
d = 1

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(p)
#s.settimeout(0.1)

def sendsnake():
    data = ""
    for e in snake:
        #data += "PX %i %i %s\nPX %i %i %s\nPX %i %i %s\n" % (e[0], e[1]-1, c, e[0], e[1], c, e[0], e[1]+1, c)
        data += "PX %i %i %s\n" % (e[0], e[1], c)
    s.sendall(bytes(data, 'ascii'))

def nextpixel(x, y):
    if d == 0:
        return (x, y+1)
    if d == 1:
        return (x+1, y)
    if d == 2:
        return (x, y-1)
    if d == 3:
        return (x-1, y)

i = 0
while True:
    i=i+1
    sendsnake()
    #sleep(0.01)
    if i > 1000:
        #print(snake)
        i=0
        # was ist die Farbe des nächsten Pixels?
        s.send(bytes("PX %i %i\n" % nextpixel(snake[-1][0], snake[-1][1]), 'ascii'))
        np = s.recv(64).split()
        nx = int(np[1])
        ny = int(np[2])
        # n = next color
        n = int("0x%s" % np[3].decode('ascii'), 16)
        # Berechne die nächste RichtungPX %i %i %s\nPX %i %i %s\n
        d = n % 4
        # Schreibe Snake neu
        #print("next PX %i %i %s\n" % (snake[0][0], snake[0][1], '000000'))
        s.sendall(bytes("PX %i %i %s\n" % (snake[0][0], snake[0][1], '000000'), 'ascii'))
        snake.pop(0)
        snake.append([nx, ny])
s.close()