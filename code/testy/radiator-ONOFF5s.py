from machine import Pin
import time

led = machine.Pin(16, machine.Pin.OUT)

while True:
    led.value(0)
    time.sleep(5)
    led.value(1)
    time.sleep(5)