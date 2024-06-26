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
import os
import re
import time
import asyncio
from bleak import BleakScanner
import bleak
from datetime import datetime

print('# bleak author:', bleak.__author__)

# デバッグ設定： Trueにすると受信したデータを標準出力に出力、Falseにするとデータをファイルに出力
DEBUG = False

# データ出力回数のカウンター
counter = 0

# 受信したデータモード1のデータを格納する変数
data_mode = 0
prev_data_mode = 0
prev_seq_no = 0

# 受信したデータをCSV形式でユニットごとに出力するフォルダ
output_folder = 'csv_files'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
output_files = []

# データを記録する間隔の設定 (advertising packet の受信なので正確な設定にはなりません)
record_interval = 60
last_record_time = {}


# 以下、プログラム・関数定義の本体

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

    if DEBUG:
        print("Data Type: 01")
        print("Sequence number: " + sequence_number)
        print("Temparature [degreeC]: " + temparature)
        print("Relative humidity [%RH]: " + relative_humidity)
        print("Ambient light [lx]: " + ambient_light)
        print("Barometric pressure [hPa]: " + barometric_pressure)
        print("Sound noise (LA) [dB]: " + sound_noise)
        print("eTVOC [ppb]: " + eTVOC)
        print("eCO2 [ppm]: " + eCO2)

    return_data = {'sequence_number': sequence_number, 
                   'temparature': temparature, 
                   'relative_humidity': relative_humidity, 
                   'ambient_light': ambient_light, 
                   'barometric_pressure': barometric_pressure, 
                   'sound_noise': sound_noise, 
                   'eTVOC': eTVOC, 
                   'eCO2': eCO2}
    return return_data

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

    if DEBUG:
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

    return_data = {'sequence_number': sequence_number,
                     'discomfort_index': discomfort_index,
                     'heat_stroke': heat_stroke,
                     'vibration_inform': vibration_inform,
                     'SI_value': SI_value,
                     'PGA': PGA,
                     'Seismic_intensity': Seismic_intensity,
                     'acceleration_x': acceleration_x,
                     'acceleration_y': acceleration_y,
                     'acceleration_z': acceleration_z}
    return return_data

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
        if DEBUG:
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

        return_data = {'sequence_number': advtype03.type1seq_no,
                     'temparature': advtype03.temparature,
                     'relative_humidity': advtype03.relative_humidity,
                     'ambient_light': advtype03.ambient_light,
                     'barometric_pressure': advtype03.barometric_pressure,
                     'sound_noise': advtype03.sound_noise,
                     'eTVOC': advtype03.eTVOC,
                     'eCO2': advtype03.eCO2,
                     'discomfort_index': advtype03.discomfort_index,
                     'heat_stroke': advtype03.heat_stroke,
                     'vibration_inform': advtype03.vibration_inform,
                     'SI_value': advtype03.SI_value,
                     'PGA': advtype03.PGA,
                     'Seismic_intensity': advtype03.Seismic_intensity,
                     'acceleration_x': advtype03.acceleration_x,
                     'acceleration_y': advtype03.acceleration_y,
                     'acceleration_z': advtype03.acceleration_z}
        
        return return_data

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
        if DEBUG:
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

        return_data = {'sequence_number': advtype04.type1seq_no,
                     'temperature_flag': advtype04.temperature_flag,
                     'relative_humidity_flag': advtype04.relative_humidity_flag,
                     'ambient_light_flag': advtype04.ambient_light_flag,
                     'barometric_pressure_flag': advtype04.barometric_pressure_flag,
                     'sound_noise_flag': advtype04.sound_noise_flag,
                     'etvoc_flag': advtype04.etvoc_flag,
                     'eco2_flag': advtype04.eco2_flag,
                     'discomfort_index_flag': advtype04.discomfort_index_flag,
                     'heat_stroke_flag': advtype04.heat_stroke_flag,
                     'si_value_flag': advtype04.si_value_flag,
                     'pga_flag': advtype04.pga_flag,
                     'seismic_intensity_flag': advtype04.seismic_intensity_flag}
        
        return return_data
 
def advtype05( data ):
    """
    print advertising packet : data type 5 (= serial number)
    """
    serial_number       = str(data[1:11])
    memory_index_latest = str(bytetoint(data[11:15], False))
    
    if DEBUG:
        print("Data Type: 05")
        print("Serial number: " + serial_number)
        print("Memory index(Latest): " + memory_index_latest)

    return_data = {'serial_number': serial_number, 'memory_index_latest': memory_index_latest}

    return return_data

def advcallback(dev, advdata):
    """
    discrimination of advertising mode  
    """
    global counter, data_mode, prev_data_mode, prev_seq_no, output_files, record_interval, last_record_time

    if ( dev.name == 'Rbt' ) :
        if ( 0x02D5 in advdata.manufacturer_data.keys() ): #0x02D5=companyID
            if DEBUG:
                print("")
                print("Address: " + dev.address)

            data = advdata.manufacturer_data[0x02D5]
            _data_dict = {}
            if data[0] == 0x01: # mode 1
                _data_dict = advtype01( data )
                _data_mode = 1
            elif data[0] == 0x02: # mode 2
                _data_dict = advtype02( data )
                _data_mode = 2
            elif data[0] == 0x03: # mode 3
                _data_dict = advtype03( data )
                _data_mode = 3
            elif data[0] == 0x04: # mode 4
                _data_dict = advtype04( data )
                _data_mode = 4
            elif data[0] == 0x05: # mode 5
                _data_dict = advtype05( data )
                _data_mode = 5
            else:
                print("unknown: " + str(data))
                _data_mode = 0

            if len(_data_dict) > 0:

                # 出力先ファイル名を生成
                device_address = re.sub(':', '', dev.address)
                if device_address not in last_record_time.keys() or (datetime.utcnow().timestamp() - last_record_time[device_address]) > record_interval:
                    last_record_time[device_address] = datetime.utcnow().timestamp()

                    _output_file = os.path.join(output_folder + '/' + device_address + '.csv')
                    if _output_file not in output_files:
                        output_files.append(_output_file)
                        print(f'出力先({len(output_files)}):', _output_file)

                    if not os.path.exists(_output_file):
                        # _data_dictのキーをCSVのヘッダーとして出力
                        _header = 'datetime,timestamp,data_mode,'+','.join(_data_dict.keys())
                    else:
                        _header = ''

                    # データ受信時刻とデバイスのアドレスと_data_dictの値を出力
                    _output = datetime.now().strftime('%Y-%m-%d %H:%M:%S')+','+str(datetime.utcnow().timestamp())+','+str(_data_mode)+','
                    _output = _output + ','.join(map(str, _data_dict.values()))

                    if prev_data_mode != _data_mode or prev_seq_no != _data_dict['sequence_number']:
                        if DEBUG:
                            if len(_header) > 0:
                                print(_output_file, '>', _header)
                            print(_output_file, '>', _output)
                        else:
                            with open(_output_file, 'a') as f:
                                if len(_header) > 0:
                                    f.write(_header + '\n')
                                f.write(_output + '\n')

                    prev_data_mode = _data_mode
                    prev_seq_no = _data_dict['sequence_number']
                    counter = counter + 1

    
            if DEBUG:
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

    print('環境センサ(2JCIE-BU01)からのデータの受信を開始... (終了は Ctrl-C を押下)')

    try:
        loop = asyncio.new_event_loop()
        while True:
            loop.run_until_complete(run())
    except KeyboardInterrupt:
        sys.exit()

