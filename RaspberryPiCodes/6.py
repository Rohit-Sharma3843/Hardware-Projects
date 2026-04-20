import board, neopixel, time

NUM = 16
pixels = neopixel.NeoPixel(board.D18, NUM, auto_write=False)

pos = 0

while True:
    pixels.fill((0,0,0))

    for i in range(5):
        idx = (pos - i) % NUM
        brightness = int(255 * (1 - i/5))
        pixels[idx] = (0, brightness, 0)

    pixels.show()
    pos = (pos + 1) % NUM
    time.sleep(0.05)
