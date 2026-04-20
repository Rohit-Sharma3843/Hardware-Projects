import paho.mqtt.client as mqtt
import json
import time
import csv
import smbus
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.cleanup()

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
    text = text[:16]  # prevent overflow
    for c in text:
        write_data(ord(c))

lcd_init()

# -------- DATA --------
nodes = {1: None, 2: None, 3: None, 4: None}

# -------- LOG --------
file = open("farm_log.csv", "a", newline="")
writer = csv.writer(file)

def log_data(node_id, temp, hum, soil, N, P, K):
    writer.writerow([time.time(), node_id, temp, hum, soil, N, P, K])
    file.flush()

# -------- DISPLAY --------
screen = 0
last_display = 0

def show_basic(i, d):
    lcd_clear()
    lcd_set_cursor(0, 0)
    lcd_print(f"N{i} S:{d.get('soil',0)}")
    lcd_set_cursor(1, 0)
    lcd_print(f"T:{d.get('temp',0):.0f} H:{d.get('hum',0):.0f}")

def show_npk(i, d):
    lcd_clear()
    lcd_set_cursor(0, 0)
    lcd_print(f"N{i} N:{d.get('N',0)} P:{d.get('P',0)}")
    lcd_set_cursor(1, 0)
    lcd_print(f"K:{d.get('K',0)}")

# -------- MQTT --------
def on_connect(client, userdata, flags, rc):
    print("Connected:", rc)
    client.subscribe("farm/data")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        node_id = data.get("id")

        if node_id not in nodes:
            return

        # SAFE DEFAULTS (important)
        data.setdefault("temp", 0)
        data.setdefault("hum", 0)
        data.setdefault("soil", 0)
        data.setdefault("N", 0)
        data.setdefault("P", 0)
        data.setdefault("K", 0)

        nodes[node_id] = data

        print(data)

        log_data(node_id,
                 data["temp"],
                 data["hum"],
                 data["soil"],
                 data["N"],
                 data["P"],
                 data["K"])

    except Exception as e:
        print("JSON ERROR:", e)

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
            screen = (screen + 1) % 8   # 2 screens per node

            node_id = (screen // 2) + 1

            if nodes[node_id]:
                if screen % 2 == 0:
                    show_basic(node_id, nodes[node_id])
                else:
                    show_npk(node_id, nodes[node_id])

except KeyboardInterrupt:
    print("Exiting...")

finally:
    file.close()
    GPIO.cleanup()
