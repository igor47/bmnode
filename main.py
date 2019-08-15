#!/usr/bin/env python

import logging

from devices import BME280, PMS7003
from log_config import log_config
from monitor import Monitor

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
