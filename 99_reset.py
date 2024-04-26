# 埼玉大学データサイエンス技術研究会 
# 第6回研究会 (2024/6/14) サンプルコード
# 作成者: 平松 薫
#
# 05_acc_2.py: 最新の加速度データを取得するプログラム #
# 
# 使い方: python 05_acc_2.py
#

import os
import sys
import time
from datetime import datetime
from struct import pack, unpack
import serial

# シリアルポートの設定
SERIAL_PORT = "COM3"
SERIAL_BAUDRATE = 115200

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
    シリアルポートにコマンドを送信する関数
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
        raise print("Invalid Header", ret)
    if ret[4] != 1 and ret[4] != 2:
        for i in range(len(ret)):
            print(f'({i}) {ret[i]:02x}', end=' ')
        print()
        raise print("Error Response", hex(ret[4]))
    return ret

# シリアルポートをオープン
ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, serial.EIGHTBITS, serial.PARITY_NONE, write_timeout=1, timeout=1)
ser.reset_input_buffer()
ser.reset_output_buffer()

payload = bytearray([0x02, # Read 0x01, Write 0x02
                    0x17, 0x51, # 4 Mode change (Address: 0x5117 をリトルエンディアンで送信)
                    0x00]) # 0x00: Normal mode (default) 0x01: Acceleration logger mode
ret = serial_read(ser, payload)


