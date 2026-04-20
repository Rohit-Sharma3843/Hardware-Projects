import board, neopixel, time, random

pixels = neopixel.NeoPixel(board.D18, 16, auto_write=False)

while True:
    pixels.fill((0,0,0))

    for _ in range(4):
        i = random.randint(0,15)
        pixels[i] = (255,255,255)

    pixels.show()
    time.sleep(0.1)
