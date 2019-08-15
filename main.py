#!/usr/bin/env python

import logging

from log_config import log_config
from monitor import Monitor

from bme280 import BME280
from PMS7003 import PMS7003

def main():
    log_config()

    log = logging.getLogger("main")
    log.info("beginning data collection")

    devices = [
        BME280(),
        PMS7003(PMS7003.S0),
    ]

    m = Monitor(devices)
    m.perform()

    log.info("monitoring complete")

if __name__ == "__main__":
    main()
