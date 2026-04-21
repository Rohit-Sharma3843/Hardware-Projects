import paho.mqtt.client as mqtt
import json
import time
import csv
import smbus
import RPi.GPIO as GPIO
from pymongo import MongoClient
from datetime import datetime, timezone
import urllib.parse

GPIO.setwarnings(False)
GPIO.cleanup()

# -------- LOGGER --------
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# -------- LCD --------
I2C_ADDR = 0x3E
bus = smbus.SMBus(1)

CMD = 0x00
DATA = 0x40

def write_cmd(cmd):
    bus.write_byte_data(I2C_ADDR, CMD, cmd)
    time.sleep(0.001)

def write_data(data):
    bus.write_byte_data(I2C_ADDR, DATA, data)
    time.sleep(0.001)

def lcd_init():
    time.sleep(0.05)
    write_cmd(0x38)
    write_cmd(0x39)
    write_cmd(0x14)
    write_cmd(0x70)
    write_cmd(0x56)
    write_cmd(0x6C)
    time.sleep(0.2)
    write_cmd(0x38)
    write_cmd(0x0C)
    write_cmd(0x01)

def lcd_clear():
    write_cmd(0x01)

def lcd_set_cursor(line, pos):
    write_cmd(0x80 + pos if line == 0 else 0xC0 + pos)

def lcd_print(text):
    text = text[:16]
    for c in text:
        write_data(ord(c))

lcd_init()
lcd_clear()
lcd_set_cursor(0, 0)
lcd_print("System Booting")
lcd_set_cursor(1, 0)
lcd_print("Please Wait...")
log("LCD Initialized")
time.sleep(2)

# -------- MONGODB (FIXED) --------
username = "spammercve_db_user"
password = urllib.parse.quote_plus("iO64WL5J8zdL1V3D")
MONGO_URI = f"mongodb+srv://{username}:{password}@cluster0.ugdr1pm.mongodb.net/?retryWrites=true&w=majority"

client_db = None
collection = None

try:
    client_db = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000
    )
    client_db.admin.command('ping')
    log("MongoDB Connected")

    db = client_db["smart_agri"]
    collection = db["sensor_data"]

except Exception as e:
    log(f"MongoDB Error: {e}")
    log("Running in OFFLINE mode (CSV only)")

# -------- NODE DATA --------
nodes = {1: None, 2: None, 3: None, 4: None}

# -------- CSV --------
file = open("farm_log.csv", "a", newline="")
writer = csv.writer(file)
log("CSV Logging Started")

def log_data(node_id, temp, hum, soil, N, P, K):
    timestamp = datetime.now(timezone.utc)

    writer.writerow([timestamp, node_id, temp, hum, soil, N, P, K])
    file.flush()

    document = {
        "timestamp": timestamp,
        "node_id": node_id,
        "temperature": temp,
        "humidity": hum,
        "soil_moisture": soil,
        "N": N,
        "P": P,
        "K": K
    }

    if collection:
        try:
            collection.insert_one(document)
            log(f"Node {node_id} inserted to MongoDB")
        except Exception as e:
            log(f"MongoDB Insert Error: {e}")
    else:
        log("MongoDB unavailable → skipping cloud save")

# -------- ULTRASONIC SENSOR --------
TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

tank_width = 10
tank_height = 100
initial_level_cm = tank_height

current_level_cm = 0
water_used_l = 0

def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.05)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        start = time.time()

    while GPIO.input(ECHO) == 1:
        end = time.time()

    return (end - start) * 17150

def update_water_usage():
    global current_level_cm, water_used_l

    d1 = get_distance()
    time.sleep(0.05)
    d2 = get_distance()
    distance = (d1 + d2) / 2

    current_level_cm = max(0, tank_height - distance)

    water_used_cm = abs(initial_level_cm - current_level_cm)

    volume_cc = water_used_cm * tank_width * tank_height
    water_used_l = volume_cc / 1000

    log(f"Water Level: {current_level_cm:.2f} cm | Used: {water_used_l:.2f} L")

# -------- DISPLAY --------
screen = 0
last_display = 0

def show_node(i, d):
    lcd_clear()
    lcd_set_cursor(0, 0)
    lcd_print(f"N{i} S:{d.get('soil',0)}%")
    lcd_set_cursor(1, 0)
    lcd_print(f"T:{d.get('temp',0):.0f} H:{d.get('hum',0):.0f}")

def show_waiting(i):
    lcd_clear()
    lcd_set_cursor(0, 0)
    lcd_print(f"N{i} Waiting...")
    lcd_set_cursor(1, 0)
    lcd_print("No Data")

def show_water_screen():
    lcd_clear()
    lcd_set_cursor(0, 0)
    lcd_print(f"Lvl:{current_level_cm:.1f}cm")
    lcd_set_cursor(1, 0)
    lcd_print(f"Used:{water_used_l:.2f}L")

# -------- MQTT --------
def on_connect(client, userdata, flags, rc):
    log(f"MQTT Connected {rc}")
    client.subscribe("farm/data")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        node_id = data.get("id")

        if node_id not in nodes:
            return

        data.setdefault("temp", 0)
        data.setdefault("hum", 0)
        data.setdefault("soil", 0)
        data.setdefault("N", 0)
        data.setdefault("P", 0)
        data.setdefault("K", 0)

        nodes[node_id] = data

        log(f"Node {node_id} -> {data}")

        log_data(node_id,
                 data["temp"],
                 data["hum"],
                 data["soil"],
                 data["N"],
                 data["P"],
                 data["K"])

    except Exception as e:
        log(f"JSON ERROR: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.137.69", 1883, 60)

# -------- MAIN LOOP --------
try:
    while True:
        client.loop(0.1)
        update_water_usage()

        now = time.time()

        if now - last_display >= 2:
            last_display = now
            screen = (screen + 1) % 5

            if screen < 4:
                node_id = screen + 1
                if nodes[node_id]:
                    show_node(node_id, nodes[node_id])
                else:
                    show_waiting(node_id)
            else:
                show_water_screen()

except KeyboardInterrupt:
    log("Stopped by User")

finally:
    GPIO.cleanup()
    file.close()
    log("System Shutdown Clean")
