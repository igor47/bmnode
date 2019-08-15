
import logging.handlers
import time
from typing import Any, Dict, List


class Monitor:
    """Repeatedly logs data from all devices"""
    LOG_OUTPUT_FILE = "/data/monitor.log"

    def __init__(self, devices: List = []):
        self.devices = devices
        self.log = logging.getLogger("monitor")

    @property
    def datalog(self) -> logging.Logger:
        if not hasattr(self, "_datalog"):
            datalog = logging.getLogger("monitor_data")

            # remove existing handlers
            datalog.handlers = []

            # add a watched file handler; we expect that logrotate will
            # rotate the output log
            handler = logging.handlers.WatchedFileHandler(self.LOG_OUTPUT_FILE)
            datalog.addHandler(handler)

            # save as root logger
            self._datalog = datalog

        return self._datalog

    def build_log_entry(self) -> Dict[str, Any]:
        """Builds a log entry from the monitored devices"""
        entry = {str(device):device.sample() for device in self.devices}
        entry['timestamp'] = time.time()

        return entry

    def perform(self) -> Dict[str, Any]:
        """Continue generating and persisting log entries"""
        while True:
            self.datalog.info(self.build_log_entry())
