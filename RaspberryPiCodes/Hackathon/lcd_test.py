from RPLCD.i2c import CharLCD
import time

lcd = CharLCD('PCF8574', 0x3E)

lcd.write_string("HELLO")
time.sleep(2)
lcd.clear()
lcd.write_string("LCD WORKS")
