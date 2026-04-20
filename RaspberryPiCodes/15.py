import board
import neopixel
import time

NUM = 16
pixels = neopixel.NeoPixel(board.D18, NUM,auto_write=False, pixel_order=neopixel.GRB)

def fade(c1, c2, steps=300, delay=0.02):
    for i in range(steps):
        r = int(c1[0] + (c2[0] - c1[0]) * i / steps)
        g = int(c1[1] + (c2[1] - c1[1]) * i / steps)
        b = int(c1[2] + (c2[2] - c1[2]) * i / steps)

        pixels.fill((r, g, b))
        pixels.show()
        time.sleep(delay)

while True:
    fade((255,0,0), (0,255,0))   # red → green
    fade((0,255,0), (0,0,255))   # green → blue
    fade((0,0,255), (255,0,0))   # blue → red
