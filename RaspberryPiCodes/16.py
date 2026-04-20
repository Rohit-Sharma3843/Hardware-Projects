import board
import neopixel
import time

pixels = neopixel.NeoPixel(
    board.D18,
    16,
    brightness=1.0,   # keep full, we control brightness manually
    auto_write=False,
    pixel_order=neopixel.GRB
)

# Define 10 colors
colors = [
    (255, 0, 0),      # red
    (0, 255, 0),      # green
    (0, 0, 255),      # blue
    (255, 20, 147),   # pink
    (255, 255, 255),  # white
    (135, 206, 235),  # sky blue
    (255, 165, 0),    # orange
    (128, 0, 128),    # purple
    (255, 255, 0),    # yellow
    (0, 255, 255)     # cyan
]

def fade_in_out(color, steps=150, delay=0.05):
    # Fade in
    for i in range(steps):
        factor = i / steps
        r = int(color[0] * factor)
        g = int(color[1] * factor)
        b = int(color[2] * factor)

        pixels.fill((r, g, b))
        pixels.show()
        time.sleep(delay)

    # Fade out
    for i in range(steps, -1, -1):
        factor = i / steps
        r = int(color[0] * factor)
        g = int(color[1] * factor)
        b = int(color[2] * factor)

        pixels.fill((r, g, b))
        pixels.show()
        time.sleep(delay)

while True:
    for color in colors:
        fade_in_out(color)
