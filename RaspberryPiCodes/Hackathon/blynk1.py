import blynklib
import RPi.GPIO as GPIO
import time

BLYNK_AUTH = 'auth_token'

GPIO.setmode(GPIO.BCM)

PIN1 = 17
PIN2 = 27
PIN3 = 22

GPIO.setup(PIN1, GPIO.OUT)
GPIO.setup(PIN2, GPIO.OUT)
GPIO.setup(PIN3, GPIO.OUT)

blynk = blynklib.Blynk(BLYNK_AUTH)

# -------- Correct Event Handling --------
def handle_virtual_write(pin, value):
    print(f"Pin {pin} Value: {value}")

    val = int(value[0])

    if pin == 0:
        GPIO.output(PIN1, val)
    elif pin == 1:
        GPIO.output(PIN2, val)
    elif pin == 2:
        GPIO.output(PIN3, val)

blynk.handle_event('write V0', lambda value: handle_virtual_write(0, value))
blynk.handle_event('write V1', lambda value: handle_virtual_write(1, value))
blynk.handle_event('write V2', lambda value: handle_virtual_write(2, value))

# -------- Main Loop --------
while True:
    blynk.run()
    time.sleep(0.01)
