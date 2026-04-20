import board, neopixel, time, math

NUM = 16
pixels = neopixel.NeoPixel(board.D18, NUM, auto_write=False)

offset = 0

while True:
    for i in range(NUM):
        val = int((math.sin((i + offset) * 0.5) + 1) * 127)
        pixels[i] = (val, 0, 255 - val)
    
    pixels.show()
    offset += 1
    time.sleep(0.05)
