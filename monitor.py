
from collections import defaultdict
import logging.handlers
import os
import time
from typing import Any, Dict, List

from devices import DeviceError

class Monitor:
    """Repeatedly logs data from all devices"""
    LOG_OUTPUT_FILE = "/data/bmnode/measurements.log"

    # avoid logging when we don't have real system time
    MIN_TIMESTAMP = 1565827200  # August 15, 2019 12:00:00 AM

    # the influxdb measurement we're outputting
    MEASUREMENT = "bmnode"

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
            try:
                os.makedirs(os.path.dirname(self.LOG_OUTPUT_FILE))
            except FileExistsError:
                pass

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

    @property
    def hostname(self) -> str:
        if not hasattr(self, "_hostname"):
            self._hostname = open("/etc/hostname").read().strip()
        return self._hostname

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

    @classmethod
    def d2str(cls, d) -> str:
        """convert dictionary of key/value pairs to a string"""
        pairs = [f"{k.replace(' ', '_')}={v}" for k,v in d.items()]
        return ",".join(pairs)

    def log_influxdb(self, fields, device) -> None:
        """logs specified fields from device in influxdb format"""
        # grab timestamp
        ts = time.time_ns()

        # add common fields we always have for all devices
        fields['read_errors'] = self.error_counts[str(device)]
        fields['uptime'] = self.uptime()
        fields['cpu_temperature'] = self.cpu_temperature()

        # generate tags
        tags = {
            'type': device.__class__.__name__,
            'id': device.id,
            'has_rtc': self.has_rtc,
            'hostname': self.hostname,
        }

        # output the log;
        # https://docs.influxdata.com/influxdb/v1.8/write_protocols/line_protocol_tutorial/
        self.datalog.info(
            f"{self.MEASUREMENT},{self.d2str(tags)} {self.d2str(fields)} {ts}"
        )

    def collect_device(self, device) -> None:
        """collects data from the specified device"""
        try:
            fields = device.sample()
        except DeviceError as e:
            self.log.warning(f"error sampling device {device}: {e}")
            self.error_counts[str(device)] += 1
        else:
            self.log_influxdb(fields, device)

    def collect_all(self) -> None:
        """collects data from the monitored devices"""
        for device in self.devices:
            self.collect_device(device)

    def perform(self) -> Dict[str, Any]:
        """Continue generating and persisting log entries"""
        while True:
            self.collect_all()
