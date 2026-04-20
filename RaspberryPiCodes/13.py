import board, neopixel, time, math

NUM = 16
pixels = neopixel.NeoPixel(board.D18, NUM, auto_write=False)

t = 0

while True:
    for i in range(NUM):
        r = int((math.sin(i*0.3 + t) + 1) * 127)
        g = int((math.sin(i*0.3 + t + 2) + 1) * 127)
        b = int((math.sin(i*0.3 + t + 4) + 1) * 127)
        pixels[i] = (r,g,b)

    pixels.show()
    t += 0.1
    time.sleep(0.05)
