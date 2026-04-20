import board, neopixel, time

NUM = 16
pixels = neopixel.NeoPixel(board.D18, NUM, auto_write=False)

pos = 0

while True:
    pixels.fill((0,0,0))

    pixels[pos] = (255,0,0)
    pixels[(pos+5)%NUM] = (0,255,0)
    pixels[(pos+10)%NUM] = (0,0,255)

    pixels.show()

    pos = (pos + 1) % NUM
    time.sleep(0.05)
