# Developed from TC-08 SINGLE MODE EXAMPLE (../picosdk-python-wrappers-master/usbtc08Examples/tc08SingleModeExample.py)
# Use streaming mode instead [see the Programmer's guide (usb-tc08-thermocouple-data-logger-programmers-guide) and
# TC-08 STREAMING MODE EXAMPLE modified by JH (../picosdk-python-wrappers-master/usbtc08Examples/tc08SingleModeExample.py)]

import ctypes
from picosdk.usbtc08 import usbtc08 as tc08
from picosdk.functions import assert_pico2000_ok

from time import sleep


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
        channels = [1]  # channels to activate
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

        # get single temperature reading
        temp = (ctypes.c_float * 9)()
        overflow = ctypes.c_int16(0)
        units = tc08.USBTC08_UNITS["USBTC08_UNITS_CENTIGRADE"]

        for inx in range(3):
            status["get_single"] = tc08.usb_tc08_get_single(
                chandle, ctypes.byref(temp), ctypes.byref(overflow), units
            )
            assert_pico2000_ok(status["get_single"])

            # print data
            print(f"Meas#{inx}: Cold Junction={temp[0]}", end=", ")
            for channel in channels:
                print(f"Channel {channel}={temp[channel]}", end=", ")
            print()
            sleep(1.5)
    except Exception as ex:
        raise ex
    finally:
        # close unit
        status["close_unit"] = tc08.usb_tc08_close_unit(chandle)
        assert_pico2000_ok(status["close_unit"])

        # display status returns
        print(status)
        print(temp)


if __name__ == "__main__":
    main()
