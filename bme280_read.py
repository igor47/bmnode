import smbus
import bme280
import time


class BME280:
    def __init__(self, port: int, address: int):
        self.port = port
        self.address = address

    @property
    def bus(self) -> smbus.SMBus:
        if not hasattr(self, "_bus"):
            self._bus = smbus.SMBus(self.port)
        return self._bus

    @property
    def calibration_params(self) -> bme280.params:
        if not hasattr(self, "_calibration_params"):
            self._calibration_params = bme280.load_calibration_params(
                self.bus, self.address
            )
        return self._calibration_params

    def sample(self) -> bme280.compensated_readings:
        return bme280.sample(self.bus, self.address, self.calibration_params)


PORT = 1
ADDRESS = 0x76

sensor = BME280(PORT, ADDRESS)

while True:
    data = sensor.sample()
    print(data.temperature)
    print(data.pressure)
    print(data.humidity)
    time.sleep(1)
