import board
import neopixel
import time
import math

pixels = neopixel.NeoPixel(board.D18, 16, auto_write=False, pixel_order=neopixel.GRB)

while True:
    for i in range(360):
        brightness = (math.sin(math.radians(i)) + 1) / 2
        val = int(255 * brightness)
        pixels.fill((val, 0, val))
        pixels.show()
        time.sleep(0.01)
