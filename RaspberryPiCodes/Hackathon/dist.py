import RPi.GPIO as GPIO
import time

# -------- SETUP --------
TRIG = 23
ECHO = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.5)

    # trigger pulse
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # wait for echo start
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    # wait for echo end
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start

    distance = pulse_duration * 17150  # cm
    return round(distance, 2)

# -------- LOOP --------
try:
    print("HC-SR04 Distance Test Started")

    while True:
        dist = get_distance()
        print(f"Distance: {dist} cm")
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopped by User")

finally:
    GPIO.cleanup()
