#!/usr/bin/python
#
# 2JCIE-BU01 environment sensor Bluetooth I/F sample
# * This program reads and display advertising packet from 2JCIE-BU01
# * intil press Ctrl-C
#
# This sample needs bleak module.
#  'python -m pip install break'
#
# This sample tested python 3.11.

import sys
import time
import asyncio
from bleak import BleakScanner


def bytetoint(buf, sig):
    """
    bytes data retrieved from 2JCIE-BU01 to integer.
    """
    return int.from_bytes(buf, byteorder='little', signed=sig)


def advtype01( data ):
    """
    print advertising packet : data type 1 (= sensor data)
    """
    sequence_number     = str(bytetoint(data[1:2], False))
    temparature         = str(bytetoint(data[2:4], True) / 100)
    relative_humidity   = str(bytetoint(data[4:6], False) / 100)
    ambient_light       = str(bytetoint(data[6:8], False))
    barometric_pressure = str(bytetoint(data[8:12], False) / 1000)
    sound_noise         = str(bytetoint(data[12:14], False) / 100)
    eTVOC               = str(bytetoint(data[14:16], False))
    eCO2                = str(bytetoint(data[16:18], False))
    print("Data Type: 01")
    print("Sequence number: " + sequence_number)
    print("Temparature [degreeC]: " + temparature)
    print("Relative humidity [%RH]: " + relative_humidity)
    print("Ambient light [lx]: " + ambient_light)
    print("Barometric pressure [hPa]: " + barometric_pressure)
    print("Sound noise (LA) [dB]: " + sound_noise)
    print("eTVOC [ppb]: " + eTVOC)
    print("eCO2 [ppm]: " + eCO2)


def advtype02( data ):
    """
    print advertising packet : data type 2 (= calcuration data)
    """
    sequence_number     = str(bytetoint(data[1:2], False))
    discomfort_index    = str(bytetoint(data[2:4], False) / 100)
    heat_stroke         = str(bytetoint(data[4:6], True) / 100)
    vibration_inform    = str(bytetoint(data[6:7], False))
    SI_value            = str(bytetoint(data[7:9], False) / 10)
    PGA                 = str(bytetoint(data[9:11], False) / 10)
    Seismic_intensity   = str(bytetoint(data[11:13], False) / 1000)
    acceleration_x      = str(bytetoint(data[13:15], True) / 10)
    acceleration_y      = str(bytetoint(data[15:17], True) / 10)
    acceleration_z      = str(bytetoint(data[17:19], True) / 10)
    print("Data Type: 02")
    print("Sequence number: " + sequence_number)
    print("Discomfort index: " + discomfort_index)
    print("Heat stroke [degreeC]: " + heat_stroke)
    print("Vibration information: " + vibration_inform)
    print("SI value [kine]: " + SI_value)
    print("PGA [gal]: " + PGA)
    print("Seismic intensity: " + Seismic_intensity)
    print("Acceleration X-dir. [gal]: " + acceleration_x)
    print("Acceleration Y-dir. [gal]: " + acceleration_y)
    print("Acceleration Z-dir. [gal]: " + acceleration_z)


def advtype03( data ):
    """
    print advertising packet : data type 3 (= sensor & calculation data)
    """
    if len(data) == 19:     # packet type 1:
        advtype03.type1seq_no         = str(bytetoint(data[1:2], False))
        advtype03.temparature         = str(bytetoint(data[2:4], True) / 100)
        advtype03.relative_humidity   = str(bytetoint(data[4:6], False) / 100)
        advtype03.ambient_light       = str(bytetoint(data[6:8], False))
        advtype03.barometric_pressure = str(bytetoint(data[8:12], False) / 1000)
        advtype03.sound_noise         = str(bytetoint(data[12:14], False) / 100)
        advtype03.eTVOC               = str(bytetoint(data[14:16], False))
        advtype03.eCO2                = str(bytetoint(data[16:18], False))
    elif len(data) == 27:   # packet type 2:
        advtype03.type2seq_no         = str(bytetoint(data[1:2], False))
        advtype03.discomfort_index    = str(bytetoint(data[2:4], False) / 100)
        advtype03.heat_stroke         = str(bytetoint(data[4:6], True) / 100)
        advtype03.vibration_inform    = str(bytetoint(data[6:7], False))
        advtype03.SI_value            = str(bytetoint(data[7:9], False) / 10)
        advtype03.PGA                 = str(bytetoint(data[9:11], False) / 10)
        advtype03.Seismic_intensity   = str(bytetoint(data[11:13], False) /1000)
        advtype03.acceleration_x      = str(bytetoint(data[13:15], True) / 10)
        advtype03.acceleration_y      = str(bytetoint(data[15:17], True) / 10)
        advtype03.acceleration_z      = str(bytetoint(data[17:19], True) / 10)

    # when both packet type 1 and 2 are recieved, display data.
    if advtype03.type1seq_no != None and advtype03.type1seq_no == advtype03.type2seq_no: 
        print("Data Type: 03")
        print("Sequence number: " + advtype03.type1seq_no)
        print("Temparature [degreeC]: " + advtype03.temparature)
        print("Relative humidity [%RH]: " + advtype03.relative_humidity)
        print("Ambient light [lx]: " + advtype03.ambient_light)
        print("Barometric pressure [hPa]: " + advtype03.barometric_pressure)
        print("Sound noise (LA) [dB]: " + advtype03.sound_noise)
        print("eTVOC [ppb]: " + advtype03.eTVOC)
        print("eCO2 [ppm]: " + advtype03.eCO2)
        print("Discomfort index: " + advtype03.discomfort_index)
        print("Heat stroke [degreeC]: " + advtype03.heat_stroke)
        print("Vibration information: " + advtype03.vibration_inform)
        print("SI value [kine]: " + advtype03.SI_value)
        print("PGA [gal]: " + advtype03.PGA)
        print("Seismic intensity: " + advtype03.Seismic_intensity)
        print("Acceleration X-dir. [gal]: " + advtype03.acceleration_x)
        print("Acceleration Y-dir. [gal]: " + advtype03.acceleration_y)
        print("Acceleration Z-dir. [gal]: " + advtype03.acceleration_z)


def advtype04( data ):
    """
    print advertising packet : data type 4 (= sensor & calculation flags)
    """
    if len(data) == 19:     # packet type 1:
        advtype04.type1seq_no              = str(bytetoint(data[1:2], False))
        advtype04.temperature_flag         = format(bytetoint(data[2:4], False), '#018b')
        advtype04.relative_humidity_flag   = format(bytetoint(data[4:6], False), '#018b')
        advtype04.ambient_light_flag       = format(bytetoint(data[6:8], False), '#018b')
        advtype04.barometric_pressure_flag = format(bytetoint(data[8:10], False), '#018b')
        advtype04.sound_noise_flag         = format(bytetoint(data[10:12], False), '#018b')
        advtype04.etvoc_flag               = format(bytetoint(data[12:14], False), '#018b')
        advtype04.eco2_flag                = format(bytetoint(data[14:16], False), '#018b')
    elif len(data) == 27:   # packet type 2:
        advtype04.type2seq_no              = str(bytetoint(data[1:2], False))
        advtype04.discomfort_index_flag    = format(bytetoint(data[2:4], False), '#018b')
        advtype04.heat_stroke_flag         = format(bytetoint(data[4:6], False), '#018b')
        advtype04.si_value_flag            = format(data[6], '#010b')
        advtype04.pga_flag                 = format(data[7], '#010b')
        advtype04.seismic_intensity_flag   = format(data[8], '#010b')

    # when both packet type 1 and 2 are recieved, display data.
    if advtype04.type1seq_no != None and advtype04.type1seq_no == advtype04.type2seq_no: 
        print("Data Type: 04")
        print("Sequence number: " + advtype04.type1seq_no)
        print("Temperature flag: " + advtype04.temperature_flag)
        print("Relative humidity flag: " + advtype04.relative_humidity_flag)
        print("Ambient light flag: " + advtype04.ambient_light_flag)
        print("Barometric pressure flag: " + advtype04.barometric_pressure_flag)
        print("Sound noise flag: " + advtype04.sound_noise_flag)
        print("eTVOC flag: " + advtype04.etvoc_flag)
        print("eCO2 flag: " + advtype04.eco2_flag)
        print("Discomfort index flag: " + advtype04.discomfort_index_flag)
        print("Heat stroke flag: " + advtype04.heat_stroke_flag)
        print("SI value flag: " + advtype04.si_value_flag)
        print("PGA flag: " + advtype04.pga_flag)
        print("Seismic intensity flag: " + advtype04.seismic_intensity_flag)

 
def advtype05( data ):
    """
    print advertising packet : data type 5 (= serial number)
    """
    serial_number       = str(data[1:11])
    memory_index_latest = str(bytetoint(data[11:15], False))
    print("Data Type: 05")
    print("Serial number: " + serial_number)
    print("Memory index(Latest): " + memory_index_latest)


def advcallback(dev, advdata):
    """
    discrimination of advertising mode  
    """
    if ( dev.name == 'Rbt' ) :
        if ( 0x02D5 in advdata.manufacturer_data.keys() ): #0x02D5=companyID
            print("")
            print("Address: " + dev.address)

            data = advdata.manufacturer_data[0x02D5]
            if data[0] == 0x01: # mode 1
                advtype01( data )
            elif data[0] == 0x02: # mode 2
                advtype02( data )
            elif data[0] == 0x03: # mode 3
                advtype03( data )
            elif data[0] == 0x04: # mode 4
                advtype04( data )
            elif data[0] == 0x05: # mode 5
                advtype05( data )
            else:
                print("unknown: " + str(data))
            print("... Press Ctrl-C to exit ...")


async def run():
    """
    scan bluetooth devices
    """
    devices = await BleakScanner.discover(timeout=1.0, scanning_mode='active', detection_callback=advcallback)


if __name__ == '__main__':
    """
    read advertising packet from 2JCIE-BU01 and display until press Ctrl-C
    """
    advtype03.type1seq_no = None
    advtype03.type2seq_no = None
    advtype04.type1seq_no = None
    advtype04.type2seq_no = None
    try:
        loop = asyncio.new_event_loop()
        while True:
            loop.run_until_complete(run())
    except KeyboardInterrupt:
        sys.exit()

