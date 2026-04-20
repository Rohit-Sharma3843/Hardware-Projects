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
I2C_ADDR = 0x3E   # change if needed after i2cdetect
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

# Boot message (CONFIRM LCD WORKING)
lcd_clear()
lcd_set_cursor(0, 0)
lcd_print("System Booting")
lcd_set_cursor(1, 0)
lcd_print("Please Wait...")
log("LCD Initialized")
time.sleep(2)

# -------- MONGODB ATLAS --------
username = "spammercve_db_user"
password = urllib.parse.quote_plus("iO64WL5J8zdL1V3D")

MONGO_URI = f"mongodb+srv://{username}:{password}@cluster0.ugdr1pm.mongodb.net/?retryWrites=true&w=majority"

client_db = MongoClient(MONGO_URI)
db = client_db["smart_agri"]
collection = db["sensor_data"]

try:
    client_db.admin.command('ping')
    log("MongoDB Atlas Connected")
except Exception as e:
    log(f"MongoDB Connection Failed: {e}")

# -------- DATA --------
nodes = {1: None, 2: None, 3: None, 4: None}

# -------- CSV LOG --------
file = open("farm_log.csv", "a", newline="")
writer = csv.writer(file)
log("CSV Logging Started")

def log_data(node_id, temp, hum, soil, N, P, K):

    timestamp = datetime.now(timezone.utc)

    # CSV
    writer.writerow([timestamp, node_id, temp, hum, soil, N, P, K])
    file.flush()

    # MongoDB
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

    try:
        collection.insert_one(document)
        log(f"Node {node_id} data inserted to MongoDB")
    except Exception as e:
        log(f"MongoDB Error: {e}")

# -------- DISPLAY --------
screen = 0
last_display = 0

def show_basic(i, d):
    lcd_clear()
    lcd_set_cursor(0, 0)
    lcd_print(f"N{i} S:{d.get('soil',0)}%")
    lcd_set_cursor(1, 0)
    lcd_print(f"T:{d.get('temp',0):.0f} H:{d.get('hum',0):.0f}")

    log(f"LCD -> Node {i} | Soil:{d.get('soil',0)} Temp:{d.get('temp',0)} Hum:{d.get('hum',0)}")

def show_waiting(i):
    lcd_clear()
    lcd_set_cursor(0, 0)
    lcd_print(f"N{i} Waiting...")
    lcd_set_cursor(1, 0)
    lcd_print("No Data")
    log(f"LCD -> Node {i} No Data")

# -------- MQTT --------
def on_connect(client, userdata, flags, rc):
    log(f"MQTT Connected with code {rc}")
    client.subscribe("farm/data")
    log("Subscribed to topic: farm/data")

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

        log(f"Data Received from Node {node_id}: {data}")

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

client.connect("192.168.137.206", 1883, 60)

# -------- LOOP --------
try:
    while True:
        client.loop(0.1)

        now = time.time()

        if now - last_display >= 2:
            last_display = now
            screen = (screen + 1) % 4

            node_id = screen + 1

            if nodes[node_id]:
                show_basic(node_id, nodes[node_id])
            else:
                show_waiting(node_id)

except KeyboardInterrupt:
    log("System Stopped by User")

finally:
    file.close()
    GPIO.cleanup()
    log("GPIO Cleaned, Program Exit")
