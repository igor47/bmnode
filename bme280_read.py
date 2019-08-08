import bme280
import logging
import logging.handlers
import smbus2 as smbus
import time
from typing import Any, Dict

from log_config import log_config, BMNodeFormatter


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
    def datalog(self) -> logging.Logger:
        if not hasattr(self, "_datalog"):
            self._datalog = logging.getLogger("bme280data")
            # rotate log file every hour by default
            handler = logging.handlers.TimedRotatingFileHandler(self.LOG_OUTPUT_FILE)
            self._datalog.addHandler(handler)
        return self._datalog

    @property
    def log(self) -> logging.Logger:
        if not hasattr(self, "_log"):
            self._log = logging.getLogger("bme280msg")
            stream = logging.StreamHandler()
            stream.setFormatter(BMNodeFormatter())
            self._log.addHandler(stream)
        return self._log

    def sample(self) -> Dict[str, Any]:
        data = bme280.sample(self.bus, self.address, self.calibration_params)
        return {
            "timestamp": data.timestamp.isoformat(),
            "temperature": data.temperature,
            "pressure": data.pressure,
            "humidity": data.humidity,
        }


PORT = 1
ADDRESS = 0x76

sensor = BME280(PORT, ADDRESS)
log_config(logging.DEBUG)

while True:
    data = sensor.sample()
    sensor.datalog.info(data)
    sensor.log.debug("got data")
    time.sleep(1)
