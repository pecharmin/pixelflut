#!/usr/bin/env python3
#coding: utf8

# TODO
# * Snake im Rahmen halten
# * Farben ausscheiden (Array analog zu snake[])

# PX <hor> <ver>

import socket
from time import sleep

p = ('192.168.11.54', 1234)
h = 1280
w = 1920
j = 9

snake = []
for i in range(int(w/2), int(w/2)+25*j, j):
    snake.append([i, int(h/2)+200])
c = '000000'
# d:
# 0: oben - y+j
# 1: rechts - x+j
# 2: unten - y-j
# 3: links - x-j
d = 1

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(p)

def sendsnake():
    data = ""
    for e in snake:
        #data += "PX %i %i %s\nPX %i %i %s\nPX %i %i %s\n" % (e[0], e[1]-1, c, e[0], e[1], c, e[0], e[1]+1, c)
        #data += "PX %i %i %s\n" % (e[0], e[1], c)
        bx = e[0]-int(j/2)
        by = e[1]-int(j/2)
        for bxi in range(0, j):
            for byi in range (0, j):
                data += "PX %i %i %s\n" % (bx+bxi, by+byi, c)
    s.sendall(bytes(data, 'ascii'))

def nextpixel(x, y):
    if d == 0:
        return (x, y+j)
    if d == 1:
        return (x+j, y)
    if d == 2:
        return (x, y-j)
    if d == 3:
        return (x-j, y)

i = 0
while True:
    i=i+1
    sendsnake()
    #sleep(0.01)
    if i > 1000:
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
        #print("next PX %i %i %s\n" % (snake[0][0], snake[0][1], '000000'))
        # Setze letzten Snake-Tail zurück
        #s.sendall(bytes("PX %i %i %s\n" % (snake[0][0], snake[0][1], '000000'), 'ascii'))
        jj=0
        while jj < j:
            jj=jj+1
            snake.pop(0)
            snake.append([nx, ny])
s.close()