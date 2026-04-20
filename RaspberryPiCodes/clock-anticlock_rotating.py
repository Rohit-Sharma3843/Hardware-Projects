import board
import neopixel
import time

NUM_PIXELS = 16
pixels = neopixel.NeoPixel(board.D18, NUM_PIXELS, auto_write=False, pixel_order=neopixel.GRB)

colors = [(255,0,0), (0,255,0), (0,0,255)]

segment = NUM_PIXELS // 3   # ~5 LEDs per color

offset = 0
direction = 1   # 1 = clockwise, -1 = anticlockwise

def show_pattern(offset):
    for i in range(NUM_PIXELS):
        color_index = ((i + offset) // segment) % 3
        pixels[i] = colors[color_index]
    pixels.show()

while True:
    show_pattern(offset)

    offset += direction

    # reverse smoothly at limits
    if offset >= NUM_PIXELS:
        direction = -1
        offset = NUM_PIXELS - 1

    elif offset < 0:
        direction = 1
        offset = 0

    time.sleep(0.05)
