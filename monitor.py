
import json
import logging.handlers
import time
from typing import Any, Dict, List

from devices import DeviceError

class Monitor:
    """Repeatedly logs data from all devices"""
    LOG_OUTPUT_FILE = "/data/monitor.log"

    # avoid logging when we don't have real system time
    MIN_TIMESTAMP = 1565827200  # August 15, 2019 12:00:00 AM

    def __init__(self, devices: List = []):
        self.devices = devices
        self.log = logging.getLogger("monitor")

    @property
    def datalog(self) -> logging.Logger:
        if not hasattr(self, "_datalog"):
            datalog = logging.getLogger("monitor.data")

            # ignore any parent loggers
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

        entry['timestamp'] = time.time()
        entry['uptime'] = self.uptime()
        entry['cpu_temperature'] = self.cpu_temperature()

        return entry

    def perform(self) -> Dict[str, Any]:
        """Continue generating and persisting log entries"""
        while True:
            entry = self.build_log_entry()

            # basic check to make sure we're not logging bullshit timestamps
            # (maybe the RTC didn't get initialized yet?)
            if entry['timestamp'] < self.MIN_TIMESTAMP:
                self.log.warning(f"timestamp {entry['timestamp']} too small")
                continue

            # log the entry
            self.datalog.info(json.dumps(entry))
