import machine
import utime
from machine import Pin


adc = machine.ADC(27)
wspolczynnik_konwersji = 100 / 65535

while True:
    rain = 100 - (adc.read_u16()* wspolczynnik_konwersji)
    print('Opady: ', rain)
    utime.sleep(1)
