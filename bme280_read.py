import bme280
import logging
import smbus2 as smbus
import time

from log_config import log_config


class BME280:
    # TODO: put this somewhere useful
    LOG_OUTPUT_FILE = "hello.log"

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

    @property
    def log(self) -> logging.Logger:
        if not hasattr(self, "_log"):
            self._log = logging.getLogger("bme280")
            handler = logging.FileHandler(self.LOG_OUTPUT_FILE)
            self._log.addHandler(handler)
        return self._log

    def sample(self) -> bme280.compensated_readings:
        return bme280.sample(self.bus, self.address, self.calibration_params)


PORT = 1
ADDRESS = 0x76

sensor = BME280(PORT, ADDRESS)
log_config(logging.DEBUG)

while True:
    data = sensor.sample()
    sensor.log.info(
        f"{data.timestamp},{data.temperature},{data.pressure},{data.humidity}"
    )
    time.sleep(1)
