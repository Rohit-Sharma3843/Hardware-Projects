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
    for c in text:
        write_data(ord(c))

lcd_init()

# -------- FLOW --------
FLOW_PIN = 17
pulse_count = 0
flow_ml_s = 0.0
total_water = 0.0

GPIO.setmode(GPIO.BCM)
GPIO.setup(FLOW_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def pulse_callback(channel):
    global pulse_count
    pulse_count += 1

GPIO.add_event_detect(FLOW_PIN, GPIO.FALLING, callback=pulse_callback)

# -------- DATA --------
nodes = {1:None, 2:None, 3:None, 4:None}

# -------- LOG --------
file = open("farm_log.csv", "a", newline="")
writer = csv.writer(file)

def log_data(node_id, temp, hum, soil):
    writer.writerow([time.time(), node_id, temp, hum, soil, flow_ml_s, total_water])
    file.flush()

# -------- DISPLAY --------
screen = 0
last_display = 0

def show_node(i, d):
    lcd_clear()
    lcd_set_cursor(0,0)
    lcd_print(f"N{i} S:{d['soil']}")
    lcd_set_cursor(1,0)
    lcd_print(f"T:{d['temp']:.0f} H:{d['hum']:.0f}")

def show_flow():
    lcd_clear()
    lcd_set_cursor(0,0)
    lcd_print(f"F:{flow_ml_s:.0f}ml/s")
    lcd_set_cursor(1,0)
    lcd_print(f"T:{total_water:.2f}L")

# -------- MQTT --------
def on_connect(client, userdata, flags, rc):
    print("Connected:", rc)
    client.subscribe("farm/data")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        node_id = data["id"]

        nodes[node_id] = data

        print(f"[NODE {node_id}] Soil:{data['soil']}")

        # 🔥 INVERTED LOGIC FIX
        if data["soil"] < 50:
            print("-> OFF")
            client.publish(f"farm/node{node_id}", "OFF")
        else:
            print("-> ON")
            client.publish(f"farm/node{node_id}", "ON")

        log_data(node_id, data["temp"], data["hum"], data["soil"])

    except Exception as e:
        print("JSON ERROR:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.137.20", 1883, 60)

# -------- LOOP --------
last_flow = time.time()

while True:
    client.loop(0.1)

    now = time.time()
    dt = now - last_flow

    if dt >= 1:
        pulses = pulse_count
        pulse_count = 0

        freq = pulses / dt
        flow_l_min = freq / 7.5
        flow_ml_s = (flow_l_min * 1000) / 60
        total_water += (flow_ml_s * dt) / 1000

        last_flow = now

    if now - last_display >= 2:
        last_display = now
        screen = (screen + 1) % 5

        if screen < 4 and nodes[screen+1]:
            show_node(screen+1, nodes[screen+1])
        else:
            show_flow()
