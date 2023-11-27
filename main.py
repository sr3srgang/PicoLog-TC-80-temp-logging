# Developed from TC-08 SINGLE MODE EXAMPLE (../picosdk-python-wrappers-master/usbtc08Examples/tc08SingleModeExample.py)
# Use streaming mode instead [see the Programmer's guide (usb-tc08-thermocouple-data-logger-programmers-guide) and
# TC-08 STREAMING MODE EXAMPLE modified by JH (../picosdk-python-wrappers-master/usbtc08Examples/tc08SingleModeExample.py)]

import ctypes
from picosdk.usbtc08 import usbtc08 as tc08
from picosdk.functions import assert_pico2000_ok

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from time import sleep
from datetime import datetime

### >>>>> User parameters >>>>>
# Measurement period
period = 15  # in second

# Temp measurement locations and assigned TC08 logger channels
assignments = [
    {
        "Location": "Exp table bottom ambient",
        "Channel": 1,
    },
    {
        "Location": "Exp table top ambient",
        "Channel": 2,
    },
    {
        "Location": "MOT coil cooling pipe in",
        "Channel": 4,
    },
    {
        "Location": "Blue laser table ambient",
        "Channel": 5,
    },
    {
        "Location": "H latt PCF input end",
        "Channel": 6,
    },
    {
        "Location": "813 IFDL breadboard",
        "Channel": 7,
    },
    {
        "Location": "813 IFDL baseplate",
        "Channel": 8,
    },
]
### <<<<< User parameters <<<<<


### should not need to touch the below

# yemonitor database credentials
url = "http://yemonitor.colorado.edu:8086"
token = "yelabtoken"
org = "yelab"

# bucket, measurement, tag, field in InfluxDB
bucket = "sr3"  # If bucket not exists, create it from the database UI.
measurement = "TC08logger"
tag = "Location"
field = "Temp[degC]"

channels = [
    assignment["Channel"] for assignment in assignments
]  # TC08 logger's channels to activate


def main():
    # Create chandle and status ready for use
    chandle = ctypes.c_int16()
    status = {}

    try:
        # open unit
        status["open_unit"] = tc08.usb_tc08_open_unit()
        assert_pico2000_ok(status["open_unit"])
        chandle = status["open_unit"]

        # set mains rejection to 60 Hz
        status["set_mains"] = tc08.usb_tc08_set_mains(chandle, 1)  # 0: 50 Hz, 1: 60 Hz
        assert_pico2000_ok(status["set_mains"])

        # set up channel
        # channels = [ assignment["Channel"] for assignment in assignments ]  # channels to activate
        # therocouples types and int8 equivalent
        # B=66 , E=69 , J=74 , K=75 , N=78 , R=82 , S=83 , T=84 , ' '=32 , X=88
        typeK = ctypes.c_int8(75)
        for channel in channels:
            status["set_channel"] = tc08.usb_tc08_set_channel(chandle, channel, typeK)
            assert_pico2000_ok(status["set_channel"])

        # get minimum sampling interval in ms
        status["get_minimum_interval_ms"] = tc08.usb_tc08_get_minimum_interval_ms(
            chandle
        )
        assert_pico2000_ok(status["get_minimum_interval_ms"])

        temp = (ctypes.c_float * 9)()
        overflow = ctypes.c_int16(0)

        # repeat measuring temps and upload to DB server
        while True:
            # get single temperature reading
            units = tc08.USBTC08_UNITS["USBTC08_UNITS_CENTIGRADE"]
            status["get_single"] = tc08.usb_tc08_get_single(
                chandle, ctypes.byref(temp), ctypes.byref(overflow), units
            )
            assert_pico2000_ok(status["get_single"])

            # print data
            datetimestr = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f"{datetimestr}: Cold Junction={temp[0]:.02f}", end=", ")
            for channel in channels:
                print(f"Ch{channel}={temp[channel]:.2f}", end=", ")
            print()

            ## upload results to yemonitor DB
            # format your data to write to the database server
            records = [
                {
                    "measurement": measurement,
                    "tags": {tag: assignment["Location"]},
                    "fields": {field: temp[assignment["Channel"]]},
                }
                for assignment in assignments
            ]

            # send the data
            with InfluxDBClient(url=url, token=token, org=org) as client:
                with client.write_api(write_options=SYNCHRONOUS) as writer:
                    writer.write(bucket=bucket, record=records)

            # wait until next period
            sleep(period)

    except Exception as ex:
        raise ex  # no handling for now

    finally:
        # close unit
        status["close_unit"] = tc08.usb_tc08_close_unit(chandle)
        assert_pico2000_ok(status["close_unit"])

        # display status returns
        print(status)
        print(temp)


if __name__ == "__main__":
    main()
