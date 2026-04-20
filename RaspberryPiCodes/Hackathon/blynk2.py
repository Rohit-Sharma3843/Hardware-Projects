import requests
import RPi.GPIO as GPIO
import time

# -------- CONFIG --------
BLYNK_AUTH = "pIdwlDpsF1Jn3HmlQ5Ast061LLAucfid"

PIN1 = 17
PIN2 = 27
PIN3 = 22

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(PIN1, GPIO.OUT)
GPIO.setup(PIN2, GPIO.OUT)
GPIO.setup(PIN3, GPIO.OUT)

def get_value(pin):
    url = f"https://blynk.cloud/external/api/get?token={BLYNK_AUTH}&{pin}"
    try:
        response = requests.get(url, timeout=2)
        return int(response.text)
    except:
        return 0

print("Running HTTP control...")

while True:
    v0 = get_value("V3")
    v1 = get_value("V1")
    v2 = get_value("V4")

    print(f"V0:{v0} V1:{v1} V2:{v2}")

    GPIO.output(PIN1, v0)
    GPIO.output(PIN2, v1)
    GPIO.output(PIN3, v2)

    time.sleep(1)
