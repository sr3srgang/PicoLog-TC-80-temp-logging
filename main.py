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
import traceback

import os
from pathlib import Path

# >>>>> User parameters >>>>>
# TC-08 Serial number
SN = "AC161/246"

# Measurement period
period = 15  # in second

# TC08 logger channels to activate & names assigned in InfluxDB
assignments = [
    {
        "num": 1,
        "name": "Ch1",
    },
    {
        "num": 2,
        "name": "Ch2",
    },
    {
        "num": 3,
        "name": "Ch3",
    },
    {
        "num": 4,
        "name": "Ch4",
    },
    {
        "num": 5,
        "name": "Ch5",
    },
    {
        "num": 6,
        "name": "Ch6",
    },
    {
        "num": 7,
        "name": "Ch7",
    },
    {
        "num": 8,
        "name": "Ch8",
    },
]

# legacy channel assignments
assignments_legacy = [
    {
        "Location": "Exp table bottom ambient",
        "Channel": 1,
    },
    {
        "Location": "Exp table top ambient",
        "Channel": 2,
    },
    {
        "Location": "MOT coil cooling pipe out",
        "Channel": 3,
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
# <<<<< User parameters <<<<<


# should not need to touch the below

# yemonitor database credentials
url = "http://yemonitor.colorado.edu:8086"
token = "yelabtoken"
org = "yelab"
bucket = "sr3"  # If bucket not exists, create it from the database UI.

channels = [
    assignment["num"] for assignment in assignments
]  # TC08 logger's channels to activate

# Names of log files
dirname_log = "./logs/"  # folder to save log files
Path(dirname_log).mkdir(exist_ok=True)

fname_log_meas = "temp.log"  # log for measure temperatures
fname_log_err = "error.log"  # log for errors


def main():
    # Create chandle and status ready for use
    chandle = ctypes.c_int16()
    status = {}  # dict to store status of device oprations; see the usages below

    try:
        # open unit
        print(f"Connecting to a TC-08 logger...")
        status["open_unit"] = tc08.usb_tc08_open_unit()
        assert_pico2000_ok(status["open_unit"])
        chandle = ctypes.c_int16(status["open_unit"])

        if status["open_unit"] != 1:  # 1 means USBTC08_OK in the Pico status codes
            raise Exception(
                f"Error: Could not open device. Error code: {status['open_unit']}\n\tcf. status=0: no (more) available device to connect.")

        print(f"Connected.")
        print()

        # set mains rejection to 60 Hz
        status["set_mains"] = tc08.usb_tc08_set_mains(
            chandle, 1)  # 0: 50 Hz, 1: 60 Hz
        assert_pico2000_ok(status["set_mains"])

        # set up channel
        # channels = [ assignment["Channel"] for assignment in assignments ]  # channels to activate
        # therocouples types and int8 equivalent
        # B=66 , E=69 , J=74 , K=75 , N=78 , R=82 , S=83 , T=84 , ' '=32 , X=88
        typeK = ctypes.c_int8(75)
        for channel in channels:
            status["set_channel"] = tc08.usb_tc08_set_channel(
                chandle, channel, typeK)
            assert_pico2000_ok(status["set_channel"])

        # get minimum sampling interval in ms
        status["get_minimum_interval_ms"] = tc08.usb_tc08_get_minimum_interval_ms(
            chandle
        )
        assert_pico2000_ok(status["get_minimum_interval_ms"])

        temp = (ctypes.c_float * 9)()
        overflow = ctypes.c_int16(0)

        # raise Exception() # error test

        # create log folder if not exist
        if not os.path.exists(dirname_log):
            os.makedirs(dirname_log)

        # repeat measuring temps and upload to DB server
        while True:
            try:
                # get single temperature reading
                units = tc08.USBTC08_UNITS["USBTC08_UNITS_CENTIGRADE"]
                status["get_single"] = tc08.usb_tc08_get_single(
                    chandle, ctypes.byref(temp), ctypes.byref(overflow), units
                )
                assert_pico2000_ok(status["get_single"])

                # raise Exception() # error test

                # print & log data
                datetimestr = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                measstr = f"{datetimestr}: Cold Junction={temp[0]:.02f}"
                for channel in channels:
                    measstr += f", Ch{channel}={temp[channel]:.2f}"

                print(measstr)

                with open(dirname_log + fname_log_meas, "a") as f:
                    f.write(measstr + "\n")

                # upload results to yemonitor DB
                # format your data to write to the database server

                records = \
                    [  # cold junction
                        {
                            "measurement": "TC08logger",
                            "tags": {
                                "Logger SN": SN,
                                "Channel": "Cold Junction",
                            },
                            "fields": {"Temp[degC]": temp[0]},
                        }
                    ] + \
                    [  # channel temperatures
                        {
                            "measurement": "TC08logger",
                            "tags": {
                                "Logger SN": SN,
                                "Channel": assignment["name"],
                            },
                            "fields": {"Temp[degC]": temp[assignment["num"]]},
                        }
                        for assignment in assignments
                    ] + \
                    [  # legacy format
                        # cold junction
                        {
                            "measurement": "TC08logger",
                            "tags": {
                                "Logger SN": SN,
                                "Location": "Cold Junction",
                            },
                            "fields": {"Temp[degC]": temp[0]},
                        }
                    ] + \
                    [  # channel temperatures
                        {
                            "measurement": "TC08logger",
                            "tags": {
                                "Logger SN": SN,
                                "Location": assignment["Location"],
                            },
                            "fields": {"Temp[degC]": temp[assignment["Channel"]]},
                        }
                        for assignment in assignments_legacy
                    ]

                # send the data
                with InfluxDBClient(url=url, token=token, org=org) as client:
                    with client.write_api(write_options=SYNCHRONOUS) as writer:
                        writer.write(bucket=bucket, record=records)

            except Exception as ex:
                datetimestr = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                measstr = f"{datetimestr}: Error occured during a measurement. See \"{dirname_log + fname_log_err}\"."
                print(measstr)
                with open(dirname_log + fname_log_meas, "a") as f:
                    f.write(measstr + "\n")

                exstr = f"{datetimestr}: Error occured during a measurement.\n"
                exstr += "".join(traceback.format_exception(ex))
                with open(dirname_log + fname_log_err, "a") as f:
                    f.write(exstr + "\n\n")

            # wait until next period
            sleep(period)

    except Exception as ex:
        datetimestr = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        exstr = f"{datetimestr}: Error occured out of the measurement loop.\n"
        exstr += "".join(traceback.format_exception(ex))
        print(exstr)

        # append error message to log file
        with open(dirname_log + fname_log_err, "a") as f:
            f.write(exstr + "\n\n")

    finally:
        # close unit
        try:
            status["close_unit"] = tc08.usb_tc08_close_unit(chandle)
            assert_pico2000_ok(status["close_unit"])
        except:
            pass

        # display status returns
        # print(status)
        # print(temp)

        print("Connection to TC-08 Logger closed. Terminating...")


if __name__ == "__main__":
    main()
