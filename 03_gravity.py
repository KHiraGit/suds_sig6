# 埼玉大学データサイエンス技術研究会 
# 第6回研究会 (2024/6/14) サンプルコード
# 作成者: 平松 薫
#
# 03_gravity.py: センサの設置方向を取得するプログラム #
# 
# 使い方: python 03_gravity.py
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
print(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

# シリアルポートをオープン (インストール状況・実行環境に応じて COM3 を変更)
ser = serial.Serial("COM3", 115200, serial.EIGHTBITS, serial.PARITY_NONE)

# センサの設置方向を取得
command = bytearray([0x52, 0x42, # Header
                     0x03, 0x00, # Length
                     0x01, # Read 0x01, Write 0x02
                     0x02, 0x54]) # 設置方向取得 (0x5402 をリトルエンディアンで送信)
command = command + calc_crc(command, len(command))
ser.write(command)
time.sleep(0.1)
ret = ser.read(ser.inWaiting())

# 取得したデータを表示
print("センサの設置方向: ", ret[6], ret)

# シリアルポートをクローズ
ser.close()
