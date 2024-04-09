#!/usr/bin/python
#
# 2JCIE-BU01 environment sensor USB I/F mode read/set sample
#
# this sample needs pyserial module.
#  'python -m pip install pyserial'
#
# this sample tested python3.11. 
#

import serial
import time
import sys
import argparse

# serial port
#SERIAL_PORT = "com3"			# Windows
#SERIAL_PORT = "/dev/ttyUSB0"		# Linux/Raspberry Pi
#SERIAL_PORT = "/dev/cuaU0"		# other Unix


def calc_crc(buf):
    """
    CRC-16 calculation.
    """
    crc = 0xFFFF
    length = len(buf)
    for i in range(length):
        crc = crc ^ buf[i]
        for i in range(8):
            carrayFlag = crc & 1
            crc = crc >> 1
            if (carrayFlag == 1):
                crc = crc ^ 0xA001
    crcH = crc >> 8
    crcL = crc & 0x00FF
    return (bytearray([crcL, crcH]))


if __name__ == '__main__':
    # argmunets parser
    parser = argparse.ArgumentParser()
    parser.add_argument("serial_port", help='serial port to which 2JCIE-BU01 is connected (comX for Windows, /dev/ttyX for linux)')
    parser.add_argument("-m", "--mode", type=int, nargs=1, help='Mode {MODE: 0=normal mode, 1=acceleration logger mode}')
    parser.add_argument("-a", "--adv", type=int, nargs=1, help='Advertising mode {ADV: 1=sensor, 2=calcuration, 3=sensor&calcuration, 4=flags, 5=serial No.}' )
    args = parser.parse_args()


    # open serial port
    try:
        ser = serial.Serial(args.serial_port, 115200, serial.EIGHTBITS, serial.PARITY_NONE)
    except:
        print( "error: serial port " + args.serial_port + " can't open." )
        sys.exit()   # error exit

    # device check
    command = bytearray([0x52, 0x42, 0x05, 0x00, 0x01, 0x0a, 0x18])
    command = command + calc_crc(command)
    ser.write(command)
    time.sleep(1)
    data = ser.read(size=ser.in_waiting)
    if len(data) != 44 or data[7:17] != b'2JCIE-BU01' : 
        print( "error: device on " + args.serial_port + " is not 2JCIE-BU01." )
        sys.exit()   # error exit

    # read/set mode/advertising mode
    try:
        # if no argument, display current mode.
        if args.mode == None and args.adv == None :
	    # read mode (address 0x5117)
            command = bytearray([0x52, 0x42, 0x05, 0x00, 0x01, 0x17, 0x51])
            command = command + calc_crc(command)
            ser.write(command)
            time.sleep(0.5)
            data = ser.read(size=ser.in_waiting)
            if data[7] == 0x00:
                print(" mode: 0 [mormal mode]")
            elif data[7] == 0x01:
                print(" mode: 1 [acceleration logger mode]")
            else:
                print(" error: unknown mode " + str(data[7]))

	    # read advertise setting (address 0x5115)
            command = bytearray([0x52, 0x42, 0x05, 0x00, 0x01, 0x15, 0x51])
            command = command + calc_crc(command)
            ser.write(command)
            time.sleep(0.5)
            data = ser.read(size=ser.in_waiting)
            if data[9] == 0x01:
                print(" advertising mode: 1 [sensor data]")
            elif data[9] == 0x02:
                print(" advertising mode: 2 [calcuration data]")
            elif data[9] == 0x03:
                print(" advertising mode: 3 [sensor & calcuration data]")
            elif data[9] == 0x04:
                print(" advertising mode: 4 [sensor & calcuration flags]")
            elif data[9] == 0x05:
                print(" advertising mode: 5 [serial number]")
            elif data[9] == 0x06:
                print(" advertising mode: 6 (reserve for future use)")
            elif data[9] == 0x07:
                print(" advertising mode: 7 (reserve for future use)")
            elif data[9] == 0x08:
                print(" advertising mode: 8 (reserve for future use)")
            else:
                print(" error: unknown advertise setting " + str(data[9]))

    	# if args.adv is not 'None', change to new advertising mode (address 0x5115)
        if args.adv != None:
	        # read current advertise setting (address 0x5115),
            # to use current 'advertising interval'.
            command = bytearray([0x52, 0x42, 0x05, 0x00, 0x01, 0x15, 0x51])
            command = command + calc_crc(command)
            ser.write(command)
            time.sleep(0.5)
            data = ser.read(size=ser.in_waiting)

            # set new advertising mode 
            command = bytearray([0x52, 0x42, 0x08, 0x00, 0x02, 0x15, 0x51])
            # data[7],data[8] are current 'advertising interval'.
            command = command + bytearray([data[7],data[8]])
            if args.adv[0] == 1:    # set sensor data mode
                command = command + bytearray([0x01])
            elif args.adv[0] == 2:  # set calcuration data mode
                command = command + bytearray([0x02])
            elif args.adv[0] == 3:  # set sensor & calcuration data mode
                command = command + bytearray([0x03])
            elif args.adv[0] == 4:  # set sensor & calcuration flags mode
                command = command + bytearray([0x04])
            elif args.adv[0] == 5:  # set serial number mode
                command = command + bytearray([0x05])
#           elif args.adv[0] == 6:      # for future use
#               command = command + bytearray([0x06])
#           elif args.adv[0] == 7:      # for future use
#               command = command + bytearray([0x07])
#           elif args.adv[0] == 8:      # for future use
#               command = command + bytearray([0x08])
            else:
                print( "error: advertising mode needs 1 to 5." )
                sys.exit()

            command = command + calc_crc(command)
            ser.write(command)
            time.sleep(0.5)
            data = ser.read(size=ser.in_waiting)

	    # if args.mode is not 'None', change to new mode (address 0x5117)
        if args.mode != None:
            if args.mode[0] == 0:   # set to normal mode
                command = bytearray([0x52, 0x42, 0x06, 0x00, 0x02, 0x17, 0x51, 0x00])
            elif args.mode[0] == 1: # set to acceleration logger mode
                command = bytearray([0x52, 0x42, 0x06, 0x00, 0x02, 0x17, 0x51, 0x01])
            else:
                print( "error: mode needs 0(=sensor mode) or 1(=acceleration logger mode)" )
                sys.exit()

            command = command + calc_crc(command)
            ser.write(command)  # blue LED turns on
            time.sleep(0.5)
            data = ser.read(size=ser.in_waiting)
            print("... now reset 2JCIE-BU01 internal memory, please wait until blue LED turns off.")

    except KeyboardInterrupt:
        sys.exit()
