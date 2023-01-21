#!/usr/bin/env python3
#coding: utf8

# TODO
# * Ausbruch der Snake in Ecken verhindern
# * Farben ausscheiden (Array analog zu snake[])
# * im Terminal anzeigen wo die Snake gerade ist (z.B. per ncurses)
# * Threading / async pixel fetch
# * Performance-Optimierungen

# Protokollformat: PX <X> <Y> <color>

from socket import socket, AF_INET, SOCK_STREAM
from time import sleep

# Pixelflut Destination Server
p = ('192.168.11.171', 1234)
# Height und Width des Pixel-Servers
h = 1280
w = 1920
# Blockgröße eines Body-Teils der Snake in Pixel, kann nur 1+2*X sein
j = 9
# Länge der Snake in Blöcken
l = 15
# Farbe der Snake
c = 'ffaaff'

# Erzeuge Blöcke für Snake Body
# Format: [[<X block 1>, <Y block 1>], [<X block 2>, <Y block 2>], ...]
# snake[-1] ist der Kopf der Snake
snake = []
for i in range(int(w/2), int(w/2)+l*j, j):
    snake.append([i, int(h/2)])

# Snake frisst Pixel und scheidet sie später wieder aus, diese werden hier gespeichert
dp = []
for i in range(0, len(snake)):
    dp.append('empty')

# Direction in welche die Snake gerade unterwegs ist?
# 0: oben   - y+j
# 1: rechts - x+j
# 2: unten  - y-j
# 3: links  - x-j
d = 1

s = socket(AF_INET, SOCK_STREAM)
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

def nextpixel(d, x, y):
    if d == 0:
        if y-j < 0:
            print('moving left')
            return nextpixel(3, x, y)
        return (x, y+j)
    if d == 1:
        if x+j > w:
            print('moving up')
            return nextpixel(0, x, y)
        return (x+j, y)
    if d == 2:
        if y+j > h:
            print('moving right')
            return nextpixel(1, x, y)
        return (x, y-j)
    if d == 3:
        if x-j < 0:
            print('moving down')
            return nextpixel(2, x, y)
        return (x-j, y)

i = 0
while True:
    i=i+1
    sendsnake()
    #sleep(0.01)
    if i > 1000:
        i=0
        # was ist die Farbe des nächsten Pixels?
        s.send(bytes("PX %i %i\n" % nextpixel(d, snake[-1][0], snake[-1][1]), 'ascii'))
        np = s.recv(64).split()
        nx = int(np[1])
        ny = int(np[2])
        print("next pixel: %i %i" % (nx, ny))
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