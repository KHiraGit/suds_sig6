# 埼玉大学データサイエンス技術研究会 
# 第6回研究会 (2024/6/14) サンプルコード
# 作成者: 平松 薫
#
# 04_acc_1.py: 最新の加速度データを取得するプログラム #
# 
# 使い方: python 04_acc_1.py
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

# シリアルポートをオープン
ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, serial.EIGHTBITS, serial.PARITY_NONE, write_timeout=1, timeout=1)

# try-except文を使って、Ctrl+C でプログラムを終了することができるようにする
try: 
    i = 0
    while ser.isOpen() and i < 100:
        # 最新加速度データを取得
        command = bytearray([0x52, 0x42, # Header
                            0x05, 0x00, # Length
                            0x01, # Read 0x01, Write 0x02
                            0x13, 0x50]) # 最新加速度データを取得 (0x5013 をリトルエンディアンで送信)
        command = command + calc_crc(command, len(command))
        ser.write(command)
        _ser_len = ser.inWaiting()
        while _ser_len == 0:
            time.sleep(0.1)
            _ser_len = ser.inWaiting()
        ret = ser.read(_ser_len)

        # 取得したデータを加速度(gal)に変換して表示
        x = s16(ret[19] | (ret[20] << 8)) * 0.1 # 加速度の単位は gal
        y = s16(ret[21] | (ret[22] << 8)) * 0.1
        z = s16(ret[23] | (ret[24] << 8)) * 0.1
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), f"x={x:.2f}, y={y:.2f}, z={z:.2f}")
        time.sleep(0.1)
        i += 1

except KeyboardInterrupt:
    # シリアルポートをクローズ
    ser.close()
