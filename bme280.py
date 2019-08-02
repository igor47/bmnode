# Code based on https://www.instructables.com/id/Raspberry-Pi-I2C-Python/
import smbus
import time

bus = smbus.SMBus(0)
address = 0x76


def bearing255():
    bear = bus.read_byte_data(address, 1)
    return bear


def bearing3599():
    bear1 = bus.read_byte_data(address, 2)
    bear2 = bus.read_byte_data(address, 3)
    bear = (bear1 << 8) + bear2
    bear = bear / 10.0
    return bear


while True:
    # return the value to 1 decimal place in degrees
    bearing = bearing3599()
    # return the value as a byte between 0 and 255
    bear255 = bearing255()
    print(bearing)
    print(bear255)
    time.sleep(1)
