import board, neopixel, time

pixels = neopixel.NeoPixel(board.D18, 16, auto_write=False)

pattern = [1,0,1,1,0,0,1,0,1,0,1,0,1,1,0,1]

while True:
    for i in range(16):
        if pattern[i]:
            pixels[i] = (0,255,0)
        else:
            pixels[i] = (0,0,0)

    pixels.show()
    time.sleep(0.3)
