#!/usr/bin/env python3
#coding: utf8

# TODO
# * Ausbruch der Snake in Ecken verhindern
# * Snake soll nur geradeaus, rechts oder links gehen können
# * Threading / async pixel fetch
# * Performance-Optimierungen
# * Rahmen definieren in dem sich die Snake bewegen darf

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

# Erzeuge Datensatz für einen Block/Body-Teil der Snake oder auszuscheidenden Pixel
# x und y bezeichnen die Mitte eines Blocks
def constructblock(x, y, c):
    data = ""
    for xi in range(0, j):
            for yi in range (0, j):
                data += "PX %i %i %s\n" % (x+xi, y+yi, c)
    return data

# Sende Snake an Pixel-Server
def sendsnake():
    data = ""
    for e in snake:
        data += constructblock(e[0]-int(j/2), e[1]-int(j/2))
    s.sendall(bytes(data, 'ascii'))

# Liefe den nächsten Pixel auf den sich die Snake bewegt,
# basierend aus der aktuellen Bewegungsrichtung und
# unter Berücksichtigung des Pixelflut-Rahmens.
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

i=0
while True:
    i=i+1
    # Sende die Snake an den Pixelflut-Server
    sendsnake()
    # Bewege die Snake regelmäßig weiter
    if i > 1000:
        i=0
        # Was ist der Inhalt des nächsten Pixels?
        s.send(bytes("PX %i %i\n" % nextpixel(d, snake[-1][0], snake[-1][1]), 'ascii'))
        np = s.recv(64).split()
        nx = int(np[1])
        ny = int(np[2])
        nc = np[3].decode('ascii')
        print("next pixel: %i %i %s" % (nx, ny, nc))
        # Berechne die nächste Richtung in welche sich die Snake bewegen soll,
        # basierend auf der Farbe des Pixels auf den sich die Snake nun bewegt.
        # Modulo 4, da es 4 Richtungen geben kann, in die sich die Snake bewegen kann.
        d = int("0x%s" % nc, 16) % 4

        # Bewege die Snake einen Block vor, indem Position des neuen Pixels ans
        # Ende des Arrays (Kopf der Snake) angefügt wird und das erste Element entfernt wird.
        snake.pop(0)
        snake.append([nx, ny])

        # Scheide ältesten gegessenen Pixel als Block aus
        s.sendall(bytes(constructblock(snake[0][0], snake[0][1], dp[0]), 'ascii'))
        dp.pop(0)
        # Füge nach oben erfolgter Bewegung der Snake den dort zuvor zu vorhandenen
        # Pixel zu den gegessenen Pixeln hinzu, damit er später ausgeschieden werden kann.
        dp.append(nc)