import smbus
import bme280
import time

PORT = 1
ADDRESS = 0x76
BUS = smbus.SMBus(PORT)

CALIBRATION_PARAMS = bme280.load_calibration_params(BUS, ADDRESS)

while True:
    data = bme280.sample(BUS, ADDRESS, CALIBRATION_PARAMS)
    print(data.temperature)
    print(data.pressure)
    print(data.humidity)
    time.sleep(1)
