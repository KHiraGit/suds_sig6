# 埼玉大学データサイエンス技術研究会 
# 第6回研究会 (2024/6/14) サンプルコード
# 作成者: 平松 薫
#
# 03_latest.py: 最新のセンサデータを取得するプログラム #
# 
# 使い方: python 03_latest.py
#

import os
import sys
import time
from datetime import datetime
from struct import pack, unpack
import serial

def calc_crc(buf, length):
    """
    CRC-16 を計算する関数

    """
    crc = 0xFFFF
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

def s16(value):
    return -(value & 0x8000) | (value & 0x7fff)

def serial_write(_ser, _payload):
    """
    環境センサにコマンドを送信する関数
    _payload の前にヘッダと_payloadの長さを付加、後に CRC-16 を付加して送信
    """
    _command = b'\x52\x42' + pack('<H', len(_payload) + 2) + _payload
    _command = _command + calc_crc(_command, len(_command))
    _ser.write(_command)
    _ser.flush()
    time.sleep(0.1)
    return

def serial_read(_ser, _payload):
    """
    環境センサにコマンドを送信し、レスポンスを取得する関数
    _payload の前にヘッダと_payloadの長さを付加、後に CRC-16 を付加して送信
    レスポンスはシリアルポートから読み込み、そのまま返す
    """
    if len(_payload) > 0:
        serial_write(_ser, _payload)
    else:
        return b''
    
    ret = _ser.read(ser.inWaiting())
    if ret[0:2] != b'\x52\x42':
        raise print("Invalid Header")
    if ret[4] != 0 and ret[4] != 1:
        raise print("Error Response", ret)
    return ret

def print_latest_data(data):
    """
    print measured latest value.
    https://github.com/omron-devhub/2jciebu-usb-raspberrypi の sample_2jciebu.py からコピー
    """
    time_measured = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    temperature = str( s16(int(hex(data[9]) + '{:02x}'.format(data[8], 'x'), 16)) / 100)
    relative_humidity = str(int(hex(data[11]) + '{:02x}'.format(data[10], 'x'), 16) / 100)
    ambient_light = str(int(hex(data[13]) + '{:02x}'.format(data[12], 'x'), 16))
    barometric_pressure = str(int(hex(data[17]) + '{:02x}'.format(data[16], 'x')
                                  + '{:02x}'.format(data[15], 'x') + '{:02x}'.format(data[14], 'x'), 16) / 1000)
    sound_noise = str(int(hex(data[19]) + '{:02x}'.format(data[18], 'x'), 16) / 100)
    eTVOC = str(int(hex(data[21]) + '{:02x}'.format(data[20], 'x'), 16))
    eCO2 = str(int(hex(data[23]) + '{:02x}'.format(data[22], 'x'), 16))
    discomfort_index = str(int(hex(data[25]) + '{:02x}'.format(data[24], 'x'), 16) / 100)
    heat_stroke = str(s16(int(hex(data[27]) + '{:02x}'.format(data[26], 'x'), 16)) / 100)
    vibration_information = str(int(hex(data[28]), 16))
    si_value = str(int(hex(data[30]) + '{:02x}'.format(data[29], 'x'), 16) / 10)
    pga = str(int(hex(data[32]) + '{:02x}'.format(data[31], 'x'), 16) / 10)
    seismic_intensity = str(int(hex(data[34]) + '{:02x}'.format(data[33], 'x'), 16) / 1000)
    temperature_flag = str(int(hex(data[36]) + '{:02x}'.format(data[35], 'x'), 16))
    relative_humidity_flag = str(int(hex(data[38]) + '{:02x}'.format(data[37], 'x'), 16))
    ambient_light_flag = str(int(hex(data[40]) + '{:02x}'.format(data[39], 'x'), 16))
    barometric_pressure_flag = str(int(hex(data[42]) + '{:02x}'.format(data[41], 'x'), 16))
    sound_noise_flag = str(int(hex(data[44]) + '{:02x}'.format(data[43], 'x'), 16))
    etvoc_flag = str(int(hex(data[46]) + '{:02x}'.format(data[45], 'x'), 16))
    eco2_flag = str(int(hex(data[48]) + '{:02x}'.format(data[47], 'x'), 16))
    discomfort_index_flag = str(int(hex(data[50]) + '{:02x}'.format(data[49], 'x'), 16))
    heat_stroke_flag = str(int(hex(data[52]) + '{:02x}'.format(data[51], 'x'), 16))
    si_value_flag = str(int(hex(data[53]), 16))
    pga_flag = str(int(hex(data[54]), 16))
    seismic_intensity_flag = str(int(hex(data[55]), 16))
    print("")
    print("Time measured:" + time_measured)
    print("Temperature:" + temperature)
    print("Relative humidity:" + relative_humidity)
    print("Ambient light:" + ambient_light)
    print("Barometric pressure:" + barometric_pressure)
    print("Sound noise:" + sound_noise)
    print("eTVOC:" + eTVOC)
    print("eCO2:" + eCO2)
    print("Discomfort index:" + discomfort_index)
    print("Heat stroke:" + heat_stroke)
    print("Vibration information:" + vibration_information)
    print("SI value:" + si_value)
    print("PGA:" + pga)
    print("Seismic intensity:" + seismic_intensity)
    print("Temperature flag:" + temperature_flag)
    print("Relative humidity flag:" + relative_humidity_flag)
    print("Ambient light flag:" + ambient_light_flag)
    print("Barometric pressure flag:" + barometric_pressure_flag)
    print("Sound noise flag:" + sound_noise_flag)
    print("eTVOC flag:" + etvoc_flag)
    print("eCO2 flag:" + eco2_flag)
    print("Discomfort index flag:" + discomfort_index_flag)
    print("Heat stroke flag:" + heat_stroke_flag)
    print("SI value flag:" + si_value_flag)
    print("PGA flag:" + pga_flag)
    print("Seismic intensity flag:" + seismic_intensity_flag)

# シリアルポートをオープン (インストール状況・実行環境に応じて COM3 を変更)
ser = serial.Serial("COM4", 115200, serial.EIGHTBITS, serial.PARITY_NONE)

# try-except文を使って、Ctrl+C でプログラムを終了することができるようにする
try: 
    i = 0
    while ser.isOpen() and i < 10:
        # 最新センサデータを取得
        payload = bytearray([0x01, # Read 0x01, Write 0x02
                             0x21, 0x50]) # 最新データを取得 (0x5021 をリトルエンディアンで送信)
        ret = serial_read(ser, payload)
        print_latest_data(ret)
        time.sleep(0.9)
        i = i + 1

except KeyboardInterrupt:
    # シリアルポートをクローズ
    ser.close()
