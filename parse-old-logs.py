#!/usr/bin/env python

from decimal import Decimal
import glob
import json
import os
import sys

from monitor import Monitor
OLD_LOG_DIR = os.path.dirname(Monitor.LOG_OUTPUT_FILE)
OLD_LOG_GLOB = f"{OLD_LOG_DIR}/monitor.log.2020*"

"""
{
    "<BME280 on 0x76>": {
        "timestamp": 1599672353.9970188, "temperature": 21.998559331987053, "pressure": 1006.811806476784, "humidity": 56.3159744993811},
    "<Diagnostics>": {
        "cpu_pct": 1.3, "cpu_load_1": 2.1, "cpu_loa d_5": 2.02, "cpu_load_15": 1.08, "mem_free_pct": 0.83076734886703, "mem_used_pct": 0.10011135669574314, "cpu_temp_c": 20.25, "net_bytes_sent": 510415211, "net_bytes_recv": 173882349, "disk_bytes_read": 321969152, "disk_bytes_write": 968504832},
    "<PMS7003 on /dev/serial0>": {
        "pm1_0_cf1": 37, "pm2_5_cf1": 55, "pm10_0_cf1": 61, "pm1_0_atm": 29, "pm2_5_atm": 44, "pm10_0_atm": 55, "count_0_3": 6069, "count_0_5": 1845, "count_1_ 0": 360, "count_2_5": 22, "count_5_0": 6, "count_10_0": 4, "checksum_errors": 273, "timestamp": 1599672354.8376982},
    "<PMS7003 on /dev/ttyUSB0>": {
        "pm1_0_cf1": 5000, "pm2_5_cf1": 5000, "pm10_0_cf1": 5000, "pm1_0_a tm": 3333, "pm2_5_atm": 3333, "pm10_0_atm": 3333, "count_0_3": 7497, "count_0_5": 2186, "count_1_0": 467, "count_2_5": 32, "count_5_0": 6, "count_10_0": 4, "checksum_errors": 0, "timestamp": 1599672353.0507863},
    "timestamp": 1599672354.8399906,
    "uptime": 162086.31,
    "cpu_temperature": 42932.0,
    "has_rtc": true
}
"""

def parse_line(line: str) -> None:
    try:
        data = json.loads(line)
    except:
        return

    time_ns = int(Decimal(data['timestamp']) * 1_000_000_000)

    for device in ["<BME280 on 0x76>", "<PMS7003 on /dev/ttyUSB0>", "<PMS7003 on /dev/serial0>"]:
        dtype, did = device.strip("<>").split(" on ")
        tags = {
            'type': dtype,
            'id': did,
            'has_rtc': data['has_rtc'],
        }

        fields = data[device]
        fields['cpu_temperature'] = data['cpu_temperature']
        fields['uptime'] = data['uptime']
        fields['read_errors'] = 0
        if "timestamp" in fields:
            del fields["timestamp"]

        print(
            f"{Monitor.MEASUREMENT},{Monitor.d2str(tags)} {Monitor.d2str(fields)} {time_ns}"
        )

def convert_file(filename: str) -> None:
    for line in open(filename).readlines():
        parse_line(line)

def convert() -> None:
    files = list(glob.glob(OLD_LOG_GLOB))
    files.sort()
    for idx, filename in enumerate(files):
        if idx % 100 == 0:
            print(f"file {idx} of {len(files)}...", file=sys.stderr)
        convert_file(filename)

if __name__ == "__main__":
    convert()
