import board
import neopixel
import time

pixels = neopixel.NeoPixel(board.D18, 30, auto_write=False, pixel_order=neopixel.GRB)

while True:
    pixels.fill((255,0,0))
    pixels.show()
    time.sleep(2)

    pixels.fill((0,255,0))
    pixels.show()
    time.sleep(2)

    pixels.fill((0,0,255))
    pixels.show()
    time.sleep(2)
