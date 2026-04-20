import board, neopixel, time, random

pixels = neopixel.NeoPixel(board.D18, 16, auto_write=False)

while True:
    for i in range(16):
        r = random.randint(180,255)
        g = random.randint(50,150)
        b = random.randint(0,30)
        pixels[i] = (r,g,b)

    pixels.show()
    time.sleep(0.08)

