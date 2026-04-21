import BlynkLib
import RPi.GPIO as GPIO
import time

print("Starting...")

# -------- GPIO SETUP --------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

PIN1 = 17
PIN2 = 27
PIN3 = 22

GPIO.setup(PIN1, GPIO.OUT)
GPIO.setup(PIN2, GPIO.OUT)
GPIO.setup(PIN3, GPIO.OUT)

# -------- AUTH --------
BLYNK_AUTH_TOKEN = "auth_token"

print("Connecting to Blynk IoT...")

blynk = BlynkLib.Blynk(
    BLYNK_AUTH_TOKEN,
    server='139.59.206.133',   # DNS bypass
    port=443
)
# -------- HANDLERS --------
def handle_v0(value):
    val = int(value[0])
    print("V0:", val)
    GPIO.output(PIN1, val)

def handle_v1(value):
    val = int(value[0])
    print("V1:", val)
    GPIO.output(PIN2, val)

def handle_v2(value):
    val = int(value[0])
    print("V2:", val)
    GPIO.output(PIN3, val)

# -------- REGISTER EVENTS --------
blynk.on("V0", handle_v0)
blynk.on("V1", handle_v1)
blynk.on("V2", handle_v2)

print("Setup complete. Running...")

# -------- LOOP --------
while True:
    try:
        blynk.run()
        time.sleep(0.01)
    except Exception as e:
        print("Error:", e)
        time.sleep(2)
