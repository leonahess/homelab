import network
import socket
import time
import rp2
from breakout_bme68x import BreakoutBME68X, STATUS_HEATER_STABLE
import gc
import micropython
import badger2040
import struct

from machine import Pin
import uasyncio as asyncio
from pimoroni_i2c import PimoroniI2C

PINS_BREAKOUT_GARDEN = {"sda": 4, "scl": 5}

onboard = Pin(15, Pin.OUT)

rp2.country('DE')
ssid = ''
password = ''

location = "Leona"
room = "Flur"

wlan = network.WLAN(network.STA_IF)

temperature = 20
humidity = 50
pressure = 1000


NTP_DELTA = 2208988800
host = "pool.ntp.org"

rtc=machine.RTC()

def set_time():
    # Get the external time reference
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()

    #Set our internal time
    val = struct.unpack("!I", msg[40:44])[0]
    tm = val - NTP_DELTA
    t = time.gmtime(tm)
    rtc.datetime((t[0],t[1],t[2],t[6]+1,t[3],t[4],t[5],0))

def start_sensor():
    # Initialize Sensor
    i2c = PimoroniI2C(**PINS_BREAKOUT_GARDEN)
    bme = BreakoutBME68X(i2c, address=0x77)

    return bme


async def read_sensor(bme, wdt):
    while True:
        wdt.feed()

        try:
            global temperature, humidity, pressure
            temperature, pressure, humidity, gas, status, _, _ = bme.read()
            now = time.gmtime()
            print("{}-{}-{} {}:{}:{} - sensor read: tmp {}°C hum {}% prs {}hPa".format(now[0], now[1], now[2],
                                                                                       now[3], now[4], now[5],
                                                                                       temperature, humidity,
                                                                                       pressure))
            await asyncio.sleep(5)
        except RuntimeError:
            now = time.gmtime()
            print("{}-{}-{} {}:{}:{} - reading sensor failed".format(now[0], now[1], now[2], now[3], now[4], now[5]))


def connect_to_network():
    wlan.active(True)
    wlan.config(pm=0xa11140)  # Disable power-save mode
    wlan.connect(ssid, password)

    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])


async def serve_client(reader, writer):
    now = time.gmtime()
    print("{}-{}-{} {}:{}:{} - Client connected".format(now[0], now[1], now[2], now[3], now[4], now[5]))
    request_line = await reader.readline()
    now = time.gmtime()
    print("{}-{}-{} {}:{}:{} - Request: {}".format(now[0], now[1], now[2], now[3], now[4], now[5], request_line))
    # We are not interested in HTTP request headers, skip them
    while await reader.readline() != b"\r\n":
        pass

    request = str(request_line)

    response = """
# HELP smarthome_temperature_celsius Sensor Temperature in celsius
# TYPE smarthome_temperature_celsius gauge
smarthome_temperature_celsius{{location="{location}",room="{room}"}} {temp}
# HELP smarthome_humidity_percent Sensor Humidity in percent
# TYPE smarthome_humidity_percent gauge
smarthome_humidity_percent{{location="{location}",room="{room}"}} {hum}
# HELP smarthome_pressure_hectopascal Sensor pressure in hPa
# TYPE smarthome_pressure_hectopascal gauge
smarthome_pressure_hectopascal{{location="{location}",room="{room}"}} {pressure}
            """.format(temp=temperature, hum=humidity, pressure=pressure / 100, location=location, room=room)

    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n')
    writer.write(response)

    await writer.drain()
    await writer.wait_closed()
    now = time.gmtime()
    print("{}-{}-{} {}:{}:{} - Client disconnected".format(now[0], now[1], now[2], now[3], now[4], now[5]))


async def update_screen(badger):
    while True:
        WIDTH, HEIGHT = badger.get_bounds()

        badger.set_pen(0)
        badger.clear()

        badger.set_pen(15)
        badger.rectangle(2, 2, WIDTH - 4, HEIGHT // 2 - 3)
        badger.rectangle(2, 65, WIDTH - 4, HEIGHT // 2 - 3)

        badger.set_pen(0)
        badger.rectangle(148, 65, 2, HEIGHT // 2)
        badger.rectangle(175, 2, 2, HEIGHT // 2 - 2)

        size = 3

        badger.set_pen(0)
        badger.set_font("bitmap14_outline")

        now = time.gmtime()

        if now[1] > 3 and now[1] < 11:
            uhrzeit = "{:02d}:{:02d}".format(now[3] + 2, now[4])
        else:
            uhrzeit = "{:02d}:{:02d}".format(now[3] + 1, now[4])

        badger.text("{}hpa".format(round(pressure / 100)), 5, 22, WIDTH, size)
        badger.text(uhrzeit, 185, 22, WIDTH, size)
        badger.text("{} °C".format(round(temperature, 1)), 5, 85, WIDTH // 2, size)
        badger.text("{} %".format(round(humidity, 1)), 155, 85, WIDTH // 2, size)

        badger.set_pen(0)
        badger.set_font("bitmap14_outline")

        badger.text("Pressure", 5, 1, WIDTH, 2)
        badger.text("Time", 185, 1, WIDTH, 2)
        badger.text("Temp", 5, 62, WIDTH, 2)
        badger.text("Humidity", 155, 62, WIDTH, 2)

        badger.update()
        await asyncio.sleep(60)


async def main():
    gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

    print('Connecting to Network...')
    connect_to_network()

    print('Intializing Sensor...')
    bme = start_sensor()

    wdt.feed()
    time.sleep(5)
    wdt.feed()

    badger = badger2040.Badger2040()
    badger.led(16)
    badger.set_update_speed(badger2040.UPDATE_NORMAL)

    print('Starting sensor thread...')
    wdt_bme = machine.WDT(timeout=8000)
    asyncio.create_task(read_sensor(bme, wdt_bme))

    print('Setting up webserver...')
    asyncio.create_task(asyncio.start_server(serve_client, "0.0.0.0", 80))

    wdt.feed()
    set_time()
    wdt.feed()

    print('Setting up screen')
    asyncio.create_task(update_screen(badger))

    while True:
        wdt.feed()

        if wlan.isconnected() == False:
            machine.reset()

        now = time.gmtime()
        print("{}-{}-{} {}:{}:{} - heartbeat".format(now[0], now[1], now[2], now[3], now[4], now[5]))

        micropython.mem_info()
        badger.led(0)
        await asyncio.sleep(0.25)

        wdt.feed()
        gc.collect()
        micropython.mem_info()
        badger.led(16)
        await asyncio.sleep(3)


wdt = machine.WDT(timeout=8000)

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()


