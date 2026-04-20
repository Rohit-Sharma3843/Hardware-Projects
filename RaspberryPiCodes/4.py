import board, neopixel, time

NUM = 16
pixels = neopixel.NeoPixel(board.D18, NUM, auto_write=False)

pos = 0
trail = 6

while True:
    pixels.fill((0,0,0))

    for i in range(trail):
        index = (pos - i) % NUM
        brightness = int(255 * (1 - i/trail))
        pixels[index] = (0, brightness, 255)

    pixels.show()
    pos = (pos + 1) % NUM
    time.sleep(0.04)
