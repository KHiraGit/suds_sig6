# 埼玉大学データサイエンス技術研究会 
# 第6回研究会 (2024/6/28) サンプルコード
# 作成者: 平松 薫
#
# 01_LED.py: LEDを点灯させるプログラム #
# 
# 使い方: python 01_LED.py
#

import os
import sys
import time
from datetime import datetime
from struct import pack, unpack
import serial

print('# serial', serial.__version__)

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

def dump_packet(_packet):
    """
    パケットのダンプを表示する関数
    """
    print(f'(len={len(_packet)})')
    for i in range(len(_packet)):
        print(f'({i}) {_packet[i]:02x}', end=' ')
        if i % 16 == 15:
            print()
    print()

def serial_write(_ser, _payload):
    """
    環境センサにコマンドを送信する関数
    _payload の前にヘッダと_payloadの長さを付加、後に CRC-16 を付加して送信
    """
    _command = b'\x52\x42' + pack('<H', len(_payload) + 2) + _payload
    _command = _command + calc_crc(_command, len(_command))
    _ser.write(_command)
    _ser.flush()
    dump_packet(_command)
    return

# 現在時刻を表示
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# シリアルポートをオープン
ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, serial.EIGHTBITS, serial.PARITY_NONE, write_timeout=1, timeout=1)

# LED を赤色で点灯
print('LEDを赤色で点灯')
payload = bytearray([0x02, # Read 0x01, Write 0x02
                     0x11, 0x51, # LED設定 (0x5111 をリトルエンディアンで送信)
                     0x01, 0x00, # LED常時点灯 (0x0001 をリトルエンディアンで送信)
                     0xff, 0x00, 0x00]) # 色設定　RGB ここでは赤に設定
serial_write(ser, payload)

# 1秒待機
time.sleep(1)

print('レスポンス')
_ser_len = ser.inWaiting()
ret = ser.read(_ser_len)
dump_packet(ret)

# 10秒待機
time.sleep(10)

# LED を消灯
print('LEDを消灯')
payload = bytearray([0x02, # Read 0x01, Write 0x02
                     0x11, 0x51, # LED設定 (0x5111 をリトルエンディアンで送信)
                     0x00, 0x00, # LED常時消灯 (0x0000 をリトルエンディアンで送信)
                     0x00, 0x00, 0x00]) # 色設定　RGB ここでは赤に設定
serial_write(ser, payload)

# 1秒待機
time.sleep(1)

print('レスポンス')
_ser_len = ser.inWaiting()
ret = ser.read(_ser_len)
dump_packet(ret)

# シリアルポートをクローズ
ser.close()
