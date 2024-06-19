import machine
import time

button = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
radiator = machine.Pin(16, machine.Pin.OUT)
led = machine.Pin(25, machine.Pin.OUT)
i = 1

led.value(1)

while True:
    first = button.value()
    time.sleep(0.01)
    second = button.value()
    if first and not second and i%2 == 1:
        print('ON:', i)
        radiator.value(1)
        i = i + 1
    elif first and not second and i%2 == 0:
        print('OFF:', i)
        radiator.value(0)
        i = i + 1