import smbus
import time

I2C_ADDR = 0x3E
bus = smbus.SMBus(1)

# Control bytes
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
    
    write_cmd(0x38)  # Function set: 8-bit, 2 line
    write_cmd(0x39)  # Extended mode
    write_cmd(0x14)  # Internal OSC freq
    write_cmd(0x70)  # Contrast low
    write_cmd(0x56)  # Power/contrast high
    write_cmd(0x6C)  # Follower control
    time.sleep(0.2)
    
    write_cmd(0x38)  # Normal mode
    write_cmd(0x0C)  # Display ON
    write_cmd(0x01)  # Clear
    time.sleep(0.01)

def lcd_clear():
    write_cmd(0x01)
    time.sleep(0.01)

def lcd_set_cursor(line, pos):
    addr = 0x80 + pos if line == 0 else 0xC0 + pos
    write_cmd(addr)

def lcd_print(text):
    for char in text:
        write_data(ord(char))

# -------- TEST --------
lcd_init()

lcd_set_cursor(0, 0)
lcd_print("HELLO")

lcd_set_cursor(1, 0)
lcd_print("LCD 0x3E WORKS")

while True:
    pass
