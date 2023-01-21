#!/usr/bin/env python3
#coding: utf8
# Erzeuge eine Snake auf einem Pixelflut-Screen, die basierend auf
# dem nächsten Pixel in ihrem Weg die Bewegungsrichtung ändert.
# Die Snake frisst die Pixel auf ihrem Weg und scheidet sie später wieder aus.

# TODO
# * Threading / async pixel fetch
# * Performance-Optimierungen
# * Parameter per CLI übergeben
# * Rahmen definieren in dem sich die Snake bewegen darf (x-y-offset, x-y-width)
# * Optionen: Snake mit jedem Schritt länger werden lassen und automatisch neustarten,
#   wenn sie sich selber fressen würde.

# Pixelflut Protokollformat: PX <X> <Y> <color>

from socket import socket, AF_INET, SOCK_STREAM
from time import sleep
from random import randint

### BEGIN settings
# Pixelflut Destination Server
p = ('192.168.11.171', 1234)
# Height und Width des Pixel-Servers
h = 1280
w = 1920
# Skalierung der Snake in Pixeln (1+2*sc)
sc = 3
# Länge der Snake in Blöcken (Block = 1 + sc * 2 Pixel)
l = 15
# Farbe der Snake
c = 'ffaaff'
# Anzahl der Print-Operationen (sendsnake) nach denen sich die Snake um einen Step/Block bewegt.
it = 5000
### EMD settings

# Blockgröße eines Body-Teils der Snake in Pixel
j = 1 + sc * 2

# Erzeuge Blöcke für Snake Body
# Format: [[<X block 1>, <Y block 1>], [<X block 2>, <Y block 2>], ...]
# snake[-1] ist der Kopf der Snake
snake = []
for i in range(int(w/2), int(w/2)+l*j, j):
    snake.append([i, int(h/2)])

# Snake frisst Pixel und scheidet sie später wieder aus, diese werden hier gespeichert.
dp = []
for i in range(0, len(snake)):
    dp.append('empty')

# d = Direction in welche die Snake gerade unterwegs ist
# 0: oben   - y+j
# 1: rechts - x+j
# 2: unten  - y-j
# 3: links  - x-j
# Beim Start wird eine zufällige Richtung ausgewählt.
d = randint(0, 3)
# Seichere die letzte Bewegunsrichtung, damit sich die Snake jeweils nur
# rechts, links und geradeaus fortbewegen kann.
ld = d

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

# Sende komplette Snake an Pixelflut-Server
def sendsnake():
    data = ""
    for e in snake:
        data += constructblock(e[0]-int(j/2), e[1]-int(j/2))
    s.sendall(bytes(data, 'ascii'))

# Liefe die Koordinate des nächsten Pixels, auf den sich die Snake bewegen soll,
# basierend aus der aktuellen Bewegungsrichtung, unter Berücksichtigung des Pixelflut-Rahmens.
def nextpixel(d, x, y):
    if d == 0:
        if y-j < 0:
            if x-j < 0:
                print('corner, moving right')
                return nextpixel(1, x, y)
            print('moving left')
            return nextpixel(3, x, y)
        return (x, y+j)
    if d == 1:
        if x+j > w:
            if y-j < 0:
                print('corner, moving down')
                return nextpixel(2, x, y)
            print('moving up')
            return nextpixel(0, x, y)
        return (x+j, y)
    if d == 2:
        if y+j > h:
            if y+j > w:
                print('corner, moving left')
                return nextpixel(3, x, y)
            print('moving right')
            return nextpixel(1, x, y)
        return (x, y-j)
    if d == 3:
        if x-j < 0:
            if y+j > h:
                print('corner, moving up')
                return nextpixel(0, x, y)
            print('moving down')
            return nextpixel(2, x, y)
        return (x-j, y)

r=0
while True:
    if r > 10000000000:
        r=0
    r=r+1

    # Sende die Snake an den Pixelflut-Server
    sendsnake()

    # Bewege die Snake regelmäßig weiter
    if r % it == 0:
        # Was ist der Inhalt des nächsten Pixels auf dem Weg der Snake?
        s.send(bytes("PX %i %i\n" % nextpixel(d, snake[-1][0], snake[-1][1]), 'ascii'))
        np = s.recv(64).split()
        nx = int(np[1])
        ny = int(np[2])
        nc = np[3].decode('ascii')
        print("next pixel: %i %i %s" % (nx, ny, nc))

        # Berechne die nächste Richtung in welche sich die Snake bewegen soll,
        # basierend auf der Farbe des Pixels auf den sich die Snake nun bewegt.
        # Modulo 4, da es 4 Richtungen geben kann, in die sich die Snake bewegen kann.
        # Speichere die bisheriger Richtung ab, damit die Snake nicht
        # den selben Weg wieder zurücknehmen kann.
        ld = d
        d = int("0x%s" % nc, 16) % 4
        # Die Snake soll nicht in die selbe Richtung zurück gehen, aus der sie kam.
        # Sie soll zufällig in eine andere Richtung gehen.
        if d == 0 && ld == 2:
            d = 1
        if d == 1 && ld == 3:
            d = 2
        if d == 2 && ld == 0:
            d = 3
        if d == 3 && ld == 1:
            d = 0

        # Definiere, dass die Snake das älteste gegessene Pixel auf dem Block
        # ausscheiden, wo sich derzeit der Tail befindet.
        # Das ausgeschiedene Pixel wird erst an den Server gesendet, wenn der Status
        # der Snake aktualisiert wurde, damit das ausgeschiedene Pixel nicht
        # von sendsnake() überschrieben wird.
        opp = constructblock(snake[0][0], snake[0][1], dp[0]

        # Bewege die Snake einen Block vor, indem Position des neuen Pixels ans
        # Ende des Arrays (Kopf der Snake) angefügt wird und das erste Element entfernt wird.
        snake.pop(0)
        snake.append([nx, ny])

        # Zeichne ältestes gegessenes Pixel als Block am Ende der Snake auf den Screen.
        s.sendall(bytes(opp), 'ascii'))

        # Entferne das ausgeschiedene Pixel aus dem Status-Array.
        dp.pop(0)
        # Füge nach oben erfolgter Bewegung der Snake den dort zuvor vorhandenen
        # Pixel zu den gegessenen Pixeln hinzu, damit er später ausgeschieden werden kann.
        dp.append(nc)