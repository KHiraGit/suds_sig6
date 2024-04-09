#!/usr/bin/python
#
# 2JCIE-BU01 environment sensor Bluetooth I/F sample
# * This program reads/set advertising mode of 2JCIE-BU01
#
# This sample needs bleak module.
#  'python -m pip install break'
#
# This sample tested python 3.9.13.

import sys
import time
import asyncio
from bleak import BleakClient
import argparse

# 2JCIE-BU01 address
#ADDRESS = "CD:C7:28:85:D3:AB"

# 2JCIE-BU01 GATT UUIDs
model_number_string_UUID = "00002A24-0000-1000-8000-00805F9B34FB"
mode_change_UUID         = "AB705117-0A3A-11E8-BA89-0ED5F89F718B"
advertise_setting_UUID   = "AB705115-0A3A-11E8-BA89-0ED5F89F718B"
flash_memory_status_UUID = "AB705403-0A3A-11E8-BA89-0ED5F89F718B"

async def waitforwrite(client):
    """
    wait for flash memory write end.
    """
    ret = bytearray([0x01])  # initial
    while ret[0] == 0x01 or ret[0] == 0x04: # loop while memory write/erase.
        time.sleep(0.5)
        ret = await client.read_gatt_char(flash_memory_status_UUID)

    if ret[0] == 0x03:  # flash memory write error
        print("error: mode set error. (flash memory write error)")


async def run():
    """
    mode read/set.
    """
    try:
        # open bluetooth client
        async with BleakClient( args.address ) as client :
            # device check
            ret = await client.read_gatt_char(model_number_string_UUID)
            if ret != b'2JCIE-BU01':
                print("Device with address " + args.address + " is not 2JCIE-BU01.")
                sys.exit()

            # if no argument, display current mode.
            if args.mode == None and args.adv == None :
                print("Address: " + args.address )
	        # check mode (UUID 0x5117)
                ret = await client.read_gatt_char(mode_change_UUID)
                if ret[0] == 0x00:
                    print(" mode: 0 [mormal mode]")
                elif ret[0] == 0x01:
                    print(" mode: 1 [acceleration logger mode]")
                else:
                    print(" error: unknown mode " + str(ret[0]))

	        # check advertise setting (UUID 0x5115)
                ret = await client.read_gatt_char(advertise_setting_UUID)
                if ret[2] == 0x01:
                    print(" advertising mode: 1 [sensor data]")
                elif ret[2] == 0x02:
                    print(" advertising mode: 2 [calcuration data]")
                elif ret[2] == 0x03:
                    print(" advertising mode: 3 [sensor & calcuration data]")
                elif ret[2] == 0x04:
                    print(" advertising mode: 4 [sensor & calcuration flags]")
                elif ret[2] == 0x05:
                    print(" advertising mode: 5 [serial number]")
                elif ret[2] == 0x06:
                    print(" advertising mode: 6 (reserve for future use)")
                elif ret[2] == 0x07:
                    print(" advertising mode: 7 (reserve for future use)")
                elif ret[2] == 0x08:
                    print(" advertising mode: 8 (reserve for future use)")
                else:
                    print(" error: unknown advertise setting " + str(ret[2]))

            # if args.adv is not 'None', change to new advertising mode (UUID 0x5115)
            if args.adv != None:
	            # read current advertise setting (UUID 0x5115)
                ret = await client.read_gatt_char(advertise_setting_UUID)
                # ret[0],ret[1] are current 'advertising interval'.

                # set new advertising mode 
                if args.adv[0] == 1:    # set sensor data mode
                    ret[2] = 0x01
                elif args.adv[0] == 2:  # set calcuration data mode
                    ret[2] = 0x02
                elif args.adv[0] == 3:  # set sensor & calcuration data mode
                    ret[2] = 0x03
                elif args.adv[0] == 4:  # set sensor & calcuration flags mode
                    ret[2] = 0x04
                elif args.adv[0] == 5:  # set serial number mode
                    ret[2] = 0x05
#               elif args.adv[0] == 6:      # for future use
#                   ret[2] = 0x06
#               elif args.adv[0] == 7:      # for future use
#                   ret[2] = 0x07
#               elif args.adv[0] == 8:      # for future use
#                   ret[2] = 0x08
                else:
                    print( "error: advertising mode needs 1 to 5." )
                    sys.exit()

                await client.write_gatt_char(advertise_setting_UUID, ret)
                await waitforwrite( client )

            # if args.mode is not 'None', change to new mode (UUID 0x5117)
            if args.mode != None:
                if args.mode[0] == 0:   # set to normal mode
                    setform = bytearray([0x00]) 
                elif args.mode[0] == 1: # set to acceleration logger mode
                    setform = bytearray([0x01]) 
                else:
                    print( "error: mode needs 0(=sensor mode) or 1(=acceleration logger mode)" )
                    sys.exit()

                await client.write_gatt_char(mode_change_UUID, setform)
                print("... resetting 2JCIE-BU01 internal memory, please wait until blue LED turns off.")
                await waitforwrite( client )

    except Exception as e:
        # bluetooth client can not open
        print("Device with address " + args.address + " was not found.")
        print(e)
        sys.exit()


if __name__ == '__main__':
    # argmunets parser
    parser = argparse.ArgumentParser()
    parser.add_argument("address", help='bluetooth address of 2JCIE-BU01 "xx:xx:xx:xx:xx:xx"')
    parser.add_argument("-m", "--mode", type=int, nargs=1, help='Mode {MODE: 0=normal mode, 1=acceleration logger mode}')
    parser.add_argument("-a", "--adv", type=int, nargs=1, help='Advertising mode {ADV: 1=sensor, 2=calcuration, 3=sensor&calcuration, 4=flags, 5=serial No.}' )
    args = parser.parse_args()

    #
    asyncio.run(run())

