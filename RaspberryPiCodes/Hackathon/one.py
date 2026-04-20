import RPi.GPIO as GPIO
import time

PIN = 17

GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def cb(channel):
    print("Pulse detected")

time.sleep(1)

GPIO.add_event_detect(PIN, GPIO.FALLING, callback=cb, bouncetime=20)

print("Listening...")
while True:
    time.sleep(1)
