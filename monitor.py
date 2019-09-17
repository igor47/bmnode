
from collections import defaultdict
import json
import logging.handlers
import os
import time
from typing import Any, Dict, List

from devices import DeviceError

class Monitor:
    """Repeatedly logs data from all devices"""
    LOG_OUTPUT_FILE = "/data/bmnode/monitor.log"

    # avoid logging when we don't have real system time
    MIN_TIMESTAMP = 1565827200  # August 15, 2019 12:00:00 AM

    def __init__(self, devices: List = []):
        self.devices = devices
        self.log = logging.getLogger("monitor")

        self.error_counts = defaultdict(lambda: 0)

    @property
    def has_rtc(self) -> bool:
        """returns whether an RTC was ever present"""
        if not hasattr(self, "_has_rtc"):
            try:
                os.stat('/dev/rtc0')
            except FileNotFoundError:
                self._has_rtc = False
            else:
                self._has_rtc = True

        return self._has_rtc

    @property
    def datalog(self) -> logging.Logger:
        if not hasattr(self, "_datalog"):
            # make sure our destination exists
            os.makedirs(os.path.dirname(self.LOG_OUTPUT_FILE))

            # grab the data logger
            datalog = logging.getLogger("monitor.data")

            # ignore any parent loggers -- these lines get written to file ONLY
            datalog.propagate = False

            # rotate the files every once in a while to allow files to close
            handler = logging.handlers.TimedRotatingFileHandler(
                self.LOG_OUTPUT_FILE, utc=True)
            datalog.addHandler(handler)

            # save as root logger
            self._datalog = datalog

        return self._datalog

    def uptime(self) -> float:
        """returns the system uptime, in seconds"""
        # keep the file open to avoid having to re-open it each time
        if not hasattr(self, '_uptime_file'):
            self._uptime_file = open('/proc/uptime', 'r')

        self._uptime_file.seek(0)
        uptime_parts = self._uptime_file.read().split()  # see `man proc`

        return float(uptime_parts[0])

    def cpu_temperature(self) -> float:
        """returns the cpu temperature"""
        if not hasattr(self, '_cpu_temp_file'):
            self._cpu_temp_file = open('/sys/class/thermal/thermal_zone0/temp', 'r')

        self._cpu_temp_file.seek(0)
        return float(self._cpu_temp_file.read().strip())

    def build_log_entry(self) -> Dict[str, Any]:
        """Builds a log entry from the monitored devices"""
        entry = {}
        for device in self.devices:
            try:
                entry[str(device)] = device.sample()
            except DeviceError as e:
                self.log.warning(f"error sampling device {device}: {e}")
                entry[str(device)] = {}
                self.error_counts[str(device)] += 1
            else:
                self.error_counts[str(device)] += 0

        entry['timestamp'] = time.time()
        entry['uptime'] = self.uptime()
        entry['cpu_temperature'] = self.cpu_temperature()
        entry['error_counts'] = self.error_counts
        entry['has_rtc'] = self.has_rtc

        return entry

    def perform(self) -> Dict[str, Any]:
        """Continue generating and persisting log entries"""
        while True:
            entry = self.build_log_entry()
            self.datalog.info(json.dumps(entry))
