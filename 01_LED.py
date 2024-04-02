# 埼玉大学データサイエンス技術研究会 
# 第6回研究会 (2024/6/14) サンプルコード
# 作成者: 平松 薫
#
# 01_LED.py: LEDを点灯させるプログラム #
# 
# 使い方: python 01_LED.py
#

import serial
import time
from datetime import datetime
import sys

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

# 現在時刻を表示
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# シリアルポートをオープン (インストール状況・実行環境に応じて COM3 を変更)
ser = serial.Serial("COM3", 115200, serial.EIGHTBITS, serial.PARITY_NONE)

# LED を赤色で点灯
command = bytearray([0x52, 0x42, # Header
                     0x0a, 0x00, # Length
                     0x02, # Read 0x01, Write 0x02
                     0x11, 0x51, # LED設定 (0x5111 をリトルエンディアンで送信)
                     0x01, 0x00, # LED常時点灯 (0x0001 をリトルエンディアンで送信)
                     0xff, 0x00, 0x00]) # 色設定　RGB ここでは赤に設定
command = command + calc_crc(command, len(command))
ser.write(command)
time.sleep(0.1)
ret = ser.read(ser.inWaiting())

# 10秒待機
time.sleep(10)

# LED を消灯
command = bytearray([0x52, 0x42, # Header
                     0x0a, 0x00, # Length
                     0x02, # Read 0x01, Write 0x02
                     0x11, 0x51, # LED設定 (0x5111 をリトルエンディアンで送信)
                     0x00, 0x00, # LED常時消灯 (0x0000 をリトルエンディアンで送信)
                     0x00, 0x00, 0x00]) # 色設定　RGB ここでは赤に設定
command = command + calc_crc(command, len(command))
ser.write(command)
time.sleep(0.1)
ret = ser.read(ser.inWaiting())

# シリアルポートをクローズ
ser.close()
