import bme280
import logging
import logging.handlers
import smbus2 as smbus
import time
from typing import Any, Dict

from i2c import BUS
from log_config import log_config, BMNodeFormatter


class BME280:
    DEFAULT_ADDRESS = 0x76

    def __init__(self, address: int = DEFAULT_ADDRESS):
        self.address = address
        self.log = logging.getLogger(str(self))

    def __str__(self):
        return f"<BME280 on #{self.id}>"

    @property
    def id(self) -> str:
        return f"0x{self.address:x}"

    @property
    def calibration_params(self) -> bme280.params:
        if not hasattr(self, "_calibration_params"):
            self._calibration_params = bme280.load_calibration_params(
                BUS, self.address
            )
        return self._calibration_params

    def sample(self) -> Dict[str, Any]:
        """returns a single reading as it should be persisted"""
        # TODO: does this raise any exceptions? can we define a timeout?
        data = bme280.sample(BUS, self.address, self.calibration_params)

        return {
            "temperature": data.temperature,
            "pressure": data.pressure,
            "humidity": data.humidity,
        }


if __name__ == "__main__":
    sensor = BME280()
    while True:
        data = sensor.sample()
        print(data)
        time.sleep(1)
