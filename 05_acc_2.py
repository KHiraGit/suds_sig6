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
        raise print("Invalid Header")
    if ret[4] != 0 and ret[4] != 1:
        raise print("Error Response", ret)
    return ret

# シリアルポートをオープン (インストール状況・実行環境に応じて COM3 を変更)
ser = serial.Serial("COM4", 115200, serial.EIGHTBITS, serial.PARITY_NONE)

# フラッシュメモリに格納されている加速度データを取得
payload = bytearray([0x01, # Read 0x01, Write 0x02
                     0x3E, 0x50, # Acceleration memory data [Header] (0x503E をリトルエンディアンで送信)
                     0x01, # Acceleration data type (0x00: Earthquake data 0x01: Vibration data)
                     0x01]) # acceleration memory index (0x01: Latest data) (0x0001 をリトルエンディアンで送信)
ret = serial_read(ser, payload)

# 取得したデータを加速度(gal)に変換して表示
page = s16(ret[7] | (ret[8] << 8))
x = s16(ret[61] | (ret[62] << 8)) * 0.1 # 加速度の単位は gal
y = s16(ret[63] | (ret[64] << 8)) * 0.1
z = s16(ret[65] | (ret[66] << 8)) * 0.1
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S %f"), f"page={page:04x}, x={x:.2f}, y={y:.2f}, z={z:.2f}")

# 最新の time counter を取得
payload = bytearray([0x01, # Read 0x01, Write 0x02
                     0x01, 0x52]) # Latest time counter (0x5201 をリトルエンディアンで送信)
ret = serial_read(ser, payload)

for i in range(len(ret)):
    print('(', i, f'{ret[i]:02x}', ret[i], ') ', end=' ')
print(ret[7:15], int.from_bytes(ret[7:8], 'little'))
current_time_counter = int.from_bytes(ret[7:8], 'little')
print()

# フラッシュメモリに格納されている加速度データを取得
payload = bytearray([0x01, # Read 0x01, Write 0x02
                     0x3E, 0x50, # Acceleration memory data [Header] (0x503E をリトルエンディアンで送信)
                     0x01, # Acceleration data type (0x00: Earthquake data 0x01: Vibration data)
                     0x01]) # acceleration memory index (0x01: Latest data) (0x0001 をリトルエンディアンで送信)
ret = serial_read(ser, payload)
for i in range(len(ret)):
    print('(', i, f'{ret[i]:02x}', ret[i], ') ', end=' ')
print()
print('total_pages', ret[8:10], int.from_bytes(ret[8:10], 'little'))
total_pages  = int.from_bytes(ret[8:10], 'little')
print('data_count', ret[10:14], int.from_bytes(ret[10:14], 'little'))
data_count  = int.from_bytes(ret[10:14], 'little')
print('data_timecounter', ret[14:22], int.from_bytes(ret[14:22], 'little'))
data_timecounter  = int.from_bytes(ret[14:22], 'little')


# シリアルポートをクローズ
ser.close()

# # try-except文を使って、Ctrl+C でプログラムを終了することができるようにする
# try: 
#     i = 0
#     while ser.isOpen() and i < 100:
#         # 最新加速度データを取得
#         command = bytearray([0x52, 0x42, # Header
#                             0x05, 0x00, # Length
#                             0x01, # Read 0x01, Write 0x02
#                             0x13, 0x50]) # 最新加速度データを取得 (0x5013 をリトルエンディアンで送信)
#         command = command + calc_crc(command, len(command))
#         ser.write(command)
#         time.sleep(0.1)
#         ret = ser.read(ser.inWaiting())

#         # 取得したデータを加速度(gal)に変換して表示
#         x = s16(ret[19] | (ret[20] << 8)) * 0.1 # 加速度の単位は gal
#         y = s16(ret[21] | (ret[22] << 8)) * 0.1
#         z = s16(ret[23] | (ret[24] << 8)) * 0.1
#         print(datetime.now().strftime("%Y-%m-%d %H:%M:%S %f"), f"x={x:.2f}, y={y:.2f}, z={z:.2f}")
#         time.sleep(0.1)
#         i += 1

# except KeyboardInterrupt:
#     # シリアルポートをクローズ
#     ser.close()
