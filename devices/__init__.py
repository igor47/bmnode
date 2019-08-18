"""convenience module for easy imports"""

class DeviceError(Exception):
    """Raised when a device encounters an error that prevents a sample from being read"""
    pass

# import other stuff so we can `from devices import`
from devices.bme280 import BME280
from devices.pms7003 import PMS7003

