from time import sleep
from machine import Pin, ADC
from servo import Servo
import dht
import utime
import math

# Deklaracja połączeń fizycznych
servoPin = Servo(pin_id=0, min_us=544.0, max_us=2400.0, min_deg=0.0, max_deg=180.0, freq=50)
dht_sensor = dht.DHT11(Pin(26))
button = Pin(12, Pin.IN, Pin.PULL_UP)
radiator = Pin(13, Pin.OUT)
led = Pin(25, Pin.OUT)
adc = ADC(27)

# Deklaracja zmiennych globalnych
wspolczynnik_konwersji = 100 / 65535
delay_ms = 0.003
led.value(1)  # LED kontrolny

def ServoRun():
    for pos in range(0, 181, 1):
        servoPin.write(pos)
        sleep(delay_ms)
    for pos in range(180, -1, -1):
        servoPin.write(pos)
        sleep(delay_ms)

def Rain_Check():
    rain = 100 - (adc.read_u16() * wspolczynnik_konwersji)
    print('Opady:', rain)
    return rain

if char == block;
    then all 

def Dew_point(T, RH):
    a = 17.625  # Wsp. Magnusa zgodne z zaleceniami Alduchova i Eskridge'a
    b = 243.05
    A = math.log(RH / 100.0)
    dew_point = (b * (A + (a * T / (b + T)))) / (a - A)
    print("Dew point:", dew_point)
    return dew_point

def DHT_Check():
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        print("temp:", temp, "hum:", hum)
        if Dew_point(temp, hum) > 20:
            return 1
        else:
            return 0
    except Exception as e:
        print("ERROR reading DHT11:", e)
        return 0

while True:
    if DHT_Check() == 1:
        radiator.value(1)
    else:
        radiator.value(0)    
    if Rain_Check() > 25:
        ServoRun()    
    utime.sleep(1)
