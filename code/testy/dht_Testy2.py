import dht
import machine
import time

sensor = dht.DHT11(machine.Pin(26))

while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        print("temp: ",temp, "hum: ", hum)
    except Exception as e:
        print("ERROR reading DHT11")
    time.sleep(1)