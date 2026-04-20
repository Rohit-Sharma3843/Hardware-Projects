import board, neopixel, time

NUM = 16
pixels = neopixel.NeoPixel(board.D18, NUM, auto_write=False)

while True:
    for i in range(NUM):
        pixels.fill((0,0,0))
        pixels[i] = (255,255,255)
        pixels.show()
        time.sleep(0.1)
