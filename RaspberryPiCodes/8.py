import board, neopixel, time

NUM = 16
pixels = neopixel.NeoPixel(board.D18, NUM, auto_write=False)

pos = 0
dir = 1

while True:
    pixels.fill((0,0,0))

    for i in range(4):
        idx = (pos - i) % NUM
        brightness = int(255 * (1 - i/4))
        pixels[idx] = (255, 0, 0)

    pixels.show()

    pos += dir
    if pos == NUM-1 or pos == 0:
        dir *= -1

    time.sleep(0.04)
