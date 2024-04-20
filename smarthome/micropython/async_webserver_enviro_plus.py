import network
import socket
import time
import rp2
import gc
import micropython

from machine import Pin
import uasyncio as asyncio
from pimoroni_i2c import PimoroniI2C
from breakout_bme280 import BreakoutBME280
from pimoroni_i2c import PimoroniI2C
from breakout_ltr559 import BreakoutLTR559
from pms5003 import PMS5003

onboard = Pin(15, Pin.OUT)

rp2.country('DE')
ssid = ''
password = ''

location = "Wand"
room = "Schlafzimmer"

wlan = network.WLAN(network.STA_IF)

temperature = 20
humidity = 50
pressure = 1000
lux = 0
prox = 0

pm1_0 = 0
pm2_5 = 0
pm10 = 0

l003 = 0
l005 = 0
l010 = 0
l025 = 0
l050 = 0
l100 = 0


def start_sensors():
    # Initialize Sensor
    i2c = PimoroniI2C(**{"sda": 2, "scl": 3})
    bme = BreakoutBME280(i2c)
    ltr = BreakoutLTR559(i2c)

    pms5003 = PMS5003(
        uart=machine.UART(1, tx=machine.Pin(4), rx=machine.Pin(5), baudrate=9600),
        pin_enable=machine.Pin(22),
        pin_reset=machine.Pin(27),
        mode="active"
    )

    return bme, ltr, pms5003


async def read_bme_sensor(bme, wdt):
    global temperature, humidity, pressure
    while True:
        wdt.feed()

        temperature, pressure, humidity = bme.read()
        print("bme sensor read")
        await asyncio.sleep(1)


async def read_light_sensor(ltr, wdt):
    global lux, prox
    while True:
        wdt.feed()

        data = ltr.get_reading()
        if data is not None:
            lux = data[BreakoutLTR559.LUX]
            prox = data[BreakoutLTR559.PROXIMITY]
            print("light sensor read")
        await asyncio.sleep(1)


async def read_pms5003_sensor(pms5003, wdt):
    global pm1_0, pm2_5, pm10, l003, l005, l010, l025, l050, l100
    while True:
        wdt.feed()

        data = pms5003.read()
        pm1_0 = data.pm_ug_per_m3(1.0)
        pm2_5 = data.pm_ug_per_m3(2.5)
        pm10 = data.pm_ug_per_m3(10)

        l003 = data.pm_per_1l_air(0.3)
        l005 = data.pm_per_1l_air(0.5)
        l010 = data.pm_per_1l_air(1.0)
        l025 = data.pm_per_1l_air(2.5)
        l050 = data.pm_per_1l_air(5)
        l100 = data.pm_per_1l_air(10)

        print("pms5003 sensor read")
        await asyncio.sleep(1)


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
# HELP smarthome_illuminance_lux Sensor illuminance in Lux
# TYPE smarthome_illuminance_lux gauge
smarthome_illuminance_lux{{location="{location}",room="{room}"}} {lux}
# HELP smarthome_particulate_matter_1_microgram_per_cubic_meter PM1 particulate matter in microgram per cubic meter
# TYPE smarthome_particulate_matter_1_microgram_per_cubic_meter gauge
smarthome_particulate_matter_1_microgram_per_cubic_meter{{location="{location}",room="{room}"}} {pm1_0}
# HELP smarthome_particulate_matter_2_5_microgram_per_cubic_meter PM2,5 particulate matter in microgram per cubic meter
# TYPE smarthome_particulate_matter_2_5_microgram_per_cubic_meter gauge
smarthome_particulate_matter_2_5_microgram_per_cubic_meter{{location="{location}",room="{room}"}} {pm2_5}
# HELP smarthome_particulate_matter_10_microgram_per_cubic_meter PM10 particulate matter in microgram per cubic meter
# TYPE smarthome_particulate_matter_10_microgram_per_cubic_meter gauge
smarthome_particulate_matter_10_microgram_per_cubic_meter{{location="{location}",room="{room}"}} {pm10}
# HELP smarthome_particles_per_300_nanometer_per_deciliter 300 nanometer sized Particles in the air per deciliter
# TYPE smarthome_particles_per_300_nanometer_per_deciliter gauge
smarthome_particles_per_300_nanometer_per_deciliter{{location="{location}",room="{room}"}} {l003}
# HELP smarthome_particles_per_500_nanometer_per_deciliter 500 nanometer sized Particles in the air per deciliter
# TYPE smarthome_particles_per_500_nanometer_per_deciliter gauge
smarthome_particles_per_500_nanometer_per_deciliter{{location="{location}",room="{room}"}} {l005}
# HELP smarthome_particles_per_1000_nanometer_per_deciliter 1000 nanometer sized Particles in the air per deciliter
# TYPE smarthome_particles_per_1000_nanometer_per_deciliter gauge
smarthome_particles_per_1000_nanometer_per_deciliter{{location="{location}",room="{room}"}} {l010}
# HELP smarthome_particles_per_2500_nanometer_per_deciliter 2500 nanometer sized Particles in the air per deciliter
# TYPE smarthome_particles_per_2500_nanometer_per_deciliter gauge
smarthome_particles_per_2500_nanometer_per_deciliter{{location="{location}",room="{room}"}} {l025}
# HELP smarthome_particles_per_5000_nanometer_per_deciliter 5000 nanometer sized Particles in the air per deciliter
# TYPE smarthome_particles_per_5000_nanometer_per_deciliter gauge
smarthome_particles_per_5000_nanometer_per_deciliter{{location="{location}",room="{room}"}} {l050}
# HELP smarthome_particles_per_10000_nanometer_per_deciliter 10000 nanometer sized Particles in the air per deciliter
# TYPE smarthome_particles_per_10000_nanometer_per_deciliter gauge
smarthome_particles_per_10000_nanometer_per_deciliter{{location="{location}",room="{room}"}} {l100}



            """.format(temp=temperature, hum=humidity, pressure=pressure / 100, lux=lux, pm1_0=pm1_0, pm2_5=pm2_5,
                       pm10=pm10, l003=l003, l005=l005, l010=l010, l025=l025, l050=l050, l100=l100, location=location,
                       room=room)

    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n')
    writer.write(response)

    await writer.drain()
    await writer.wait_closed()
    now = time.gmtime()
    print("{}-{}-{} {}:{}:{} - Client disconnected".format(now[0], now[1], now[2], now[3], now[4], now[5]))


async def main(wdt):
    gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

    print('Connecting to Network...')
    connect_to_network()

    print('Intializing Sensors...')
    bme, ltr, pms5003 = start_sensors()

    wdt.feed()
    time.sleep(5)
    wdt.feed()

    print('Starting bme sensor thread...')
    wdt_bme = machine.WDT(timeout=8000)
    asyncio.create_task(read_bme_sensor(bme, wdt_bme))

    print('Starting light sensor thread...')
    wdt_ltr = machine.WDT(timeout=8000)
    asyncio.create_task(read_light_sensor(ltr, wdt_ltr))

    print('Starting pms5003 sensor thread...')
    wdt_pms = machine.WDT(timeout=8000)
    asyncio.create_task(read_pms5003_sensor(pms5003, wdt_pms))

    print('Setting up webserver...')
    asyncio.create_task(asyncio.start_server(serve_client, "0.0.0.0", 80))

    while True:
        wdt.feed()

        if wlan.isconnected() == False:
            machine.reset()
        now = time.gmtime()
        print("{}-{}-{} {}:{}:{} - heartbeat".format(now[0], now[1], now[2], now[3], now[4], now[5]))

        micropython.mem_info()
        await asyncio.sleep(0.25)

        wdt.feed()
        gc.collect()
        micropython.mem_info()
        await asyncio.sleep(5)


wdt = machine.WDT(timeout=8000)

try:
    asyncio.run(main(wdt))
finally:
    asyncio.new_event_loop()

