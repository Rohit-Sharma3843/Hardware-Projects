import board
import neopixel
import time

pixels = neopixel.NeoPixel(board.D18, 30, auto_write=False, pixel_order=neopixel.GRB)

def fade_color(r1, g1, b1, r2, g2, b2, steps=100, delay=0.02):
    for i in range(steps):
        r = int(r1 + (r2 - r1) * i / steps)
        g = int(g1 + (g2 - g1) * i / steps)
        b = int(b1 + (b2 - b1) * i / steps)
        pixels.fill((r, g, b))
        pixels.show()
        time.sleep(delay)

while True:
    fade_color(255,0,0, 0,255,0)   # red → green
    fade_color(0,255,0, 0,0,255)   # green → blue
    fade_color(0,0,255, 255,0,0)   # blue → red
