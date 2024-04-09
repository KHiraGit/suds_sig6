#!/usr/bin/python
#
# 2JCIE-BU01 environment sensor USB I/F sample
# * This program reads and displays envrionment data from 2JCIE-BU01 
# * until press Ctrl-C.
#
# this sample needs pyserial module.
#  'python -m pip install pyserial'
#
# this sample tested python3.11 . 
#

import serial
import time
from datetime import datetime
import sys
import argparse

# serial port
#	Check your system to find the correct name
#SERIAL_PORT = "com3"			# Windows
#SERIAL_PORT = "/dev/ttyUSB0"		# Linux/Raspberry Pi
#SERIAL_PORT = "/dev/cuaU0"		# other Unix

def bytetoint(buf,sig):
    """
    bytes data retrieved from 2JCIE-BU01 to integer.
    """
    return int.from_bytes(buf, byteorder='little', signed=sig)


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


def print_latest_data(data):
    """
    print measured latest value.
    """
    time_measured = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    temperature	          = str(bytetoint(data[8:10], True) / 100)
    relative_humidity     = str(bytetoint(data[10:12], False) / 100)
    ambient_light         = str(bytetoint(data[12:14], False))
    barometric_pressure   = str(bytetoint(data[14:18], False) / 1000)
    sound_noise           = str(bytetoint(data[18:20], False) / 100)
    eTVOC                 = str(bytetoint(data[20:22], False))
    eCO2                  = str(bytetoint(data[22:24], False))
    discomfort_index      = str(bytetoint(data[24:26], False) / 100)
    heat_stroke           = str(bytetoint(data[26:28], True) / 100)
    vibration_information = str(bytetoint(data[28:29], False))
    si_value              = str(bytetoint(data[29:31], False) / 10)
    pga                   = str(bytetoint(data[31:33], False) / 10)
    seismic_intensity     = str(bytetoint(data[33:35], False) / 1000)

    temperature_flag         = format(bytetoint(data[35:37], False), '#018b')
    relative_humidity_flag   = format(bytetoint(data[37:39], False), '#018b')
    ambient_light_flag       = format(bytetoint(data[39:41], False), '#018b')
    barometric_pressure_flag = format(bytetoint(data[41:43], False), '#018b')
    sound_noise_flag         = format(bytetoint(data[43:45], False), '#018b')
    etvoc_flag               = format(bytetoint(data[45:47], False), '#018b')
    eco2_flag                = format(bytetoint(data[47:49], False), '#018b')
    discomfort_index_flag    = format(bytetoint(data[49:51], False), '#018b')
    heat_stroke_flag         = format(bytetoint(data[51:53], False), '#018b')
    si_value_flag            = format(data[53], '#010b')
    pga_flag                 = format(data[54], '#010b')
    seismic_intensity_flag   = format(data[55], '#010b')

    print("")
    print("Time measured: " + time_measured)
    print("Temperature [degreeC]: " + temperature)
    print("Relative humidity [%RH]: " + relative_humidity)
    print("Ambient light [lx]: " + ambient_light)
    print("Barometric pressure [hPa]: " + barometric_pressure)
    print("Sound noise (LA) [dB]: " + sound_noise)
    print("eTVOC [ppb]: " + eTVOC)
    print("eCO2 [ppm]: " + eCO2)
    print("Discomfort index: " + discomfort_index)
    print("Heat stroke [degreeC]: " + heat_stroke)
    print("Vibration information: " + vibration_information)
    print("SI value [kine]: " + si_value)
    print("PGA [gal]: " + pga)
    print("Seismic intensity: " + seismic_intensity)
    print("Temperature flag: " + temperature_flag)
    print("Relative humidity flag: " + relative_humidity_flag)
    print("Ambient light flag: " + ambient_light_flag)
    print("Barometric pressure flag: " + barometric_pressure_flag)
    print("Sound noise flag: " + sound_noise_flag)
    print("eTVOC flag: " + etvoc_flag)
    print("eCO2 flag: " + eco2_flag)
    print("Discomfort index flag: " + discomfort_index_flag)
    print("Heat stroke flag: " + heat_stroke_flag)
    print("SI value flag: " + si_value_flag)
    print("PGA flag: " + pga_flag)
    print("Seismic intensity flag: " + seismic_intensity_flag)

    print("... Press Ctrl-C to exit ...")


def set_led(flag):
    """
    LED on/off.  flag==0 -> LED off, flag!=0 -> LED on  (address: 0x5111)
    """
    if flag == 0:
        #   command LED off 
        command = bytearray([0x52, 0x42, 0x0a, 0x00, 0x02, 0x11, 0x51, 0, 0x00, 0, 0, 0])
    else:
        #   command LED on, color : green
        command = bytearray([0x52, 0x42, 0x0a, 0x00, 0x02, 0x11, 0x51, 1, 0x00, 0, 255, 0])

    command = command + calc_crc(command)
    ser.write(command)
    time.sleep(0.1)
    ret = ser.read(size=14)


if __name__ == '__main__':
    # argmunets parser
    parser = argparse.ArgumentParser()
    parser.add_argument("serial_port", help='serial port to which 2JCIE-BU01 is connected (comX for Windows, /dev/ttyX for linux)')
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
    ret = ser.read(size=ser.in_waiting)
    if len(ret) != 44 or ret[7:17] != b'2JCIE-BU01' : 
        print( "error: device on " + args.serial_port + " is not 2JCIE-BU01." )
        sys.exit()   # error exit

    # read environment data
    try:
        # LED on
        set_led(1)
        time.sleep(1)
        # LED off
        set_led(0)

        while ser.isOpen():
            # Get Latest data Long. (address 0x5021)
            command = bytearray([0x52, 0x42, 0x05, 0x00, 0x01, 0x21, 0x50])
            command = command + calc_crc(command)
            tmp = ser.write(command)
            time.sleep(0.1)
            data = ser.read(size=ser.in_waiting)
            print_latest_data(data)
            time.sleep(1)

    except KeyboardInterrupt:
        # LED on
        set_led(1)
        time.sleep(1)
        # LED off
        set_led(0)

        sys.exit()
