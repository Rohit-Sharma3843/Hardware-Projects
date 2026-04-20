import board, neopixel, time

NUM = 16
pixels = neopixel.NeoPixel(board.D18, NUM, auto_write=False)

center = 0

while True:
    for r in range(NUM//2):
        pixels.fill((0,0,0))

        pixels[(center + r) % NUM] = (255,100,0)
        pixels[(center - r) % NUM] = (255,100,0)

        pixels.show()
        time.sleep(0.05)

    center = (center + 1) % NUM
