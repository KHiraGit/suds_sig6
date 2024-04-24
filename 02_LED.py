# 埼玉大学データサイエンス技術研究会 
# 第6回研究会 (2024/6/14) サンプルコード
# 作成者: 平松 薫
#
# 02_LED.py: LEDを点灯させるプログラム #
# 
# 使い方: python 02_LED.py
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

def serial_write(_ser, _payload):
    """
    環境センサにコマンドを送信する関数
    _payload の前にヘッダと_payloadの長さを付加、後に CRC-16 を付加して送信
    """
    _command = b'\x52\x42' + pack('<H', len(_payload) + 2) + _payload
    _command = _command + calc_crc(_command, len(_command))
    _ser.write(_command)
    _ser.flush()
    return

def led_off(_ser):
    """
    LEDを消灯する関数
    """
    _payload = bytearray([0x02, # Read 0x01, Write 0x02
                          0x11, 0x51, # LED設定 (0x5111 をリトルエンディアンで送信)
                          0x00, 0x00, # LED常時消灯 (0x0000 をリトルエンディアンで送信)
                          0x00, 0x00, 0x00]) # 色設定　RGB ここでは赤に設定
    serial_write(_ser, _payload)
    return

def led_on_illuminance(_ser):
    """
    LEDを点灯する関数
    """
    _payload = bytearray([0x02, # Read 0x01, Write 0x02
                          0x11, 0x51, # LED設定 (0x5111 をリトルエンディアンで送信)
                          0x04, 0x00, # 照度センサで色を変更 (0x0004 をリトルエンディアンで送信)
                          0x00, 0x00, 0x00]) # 色設定　RGB ここでは赤に設定
    serial_write(_ser, _payload)

# 現在時刻を表示
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# シリアルポートをオープン (インストール状況・実行環境に応じて COM3 を変更)
ser = serial.Serial("COM3", 115200, serial.EIGHTBITS, serial.PARITY_NONE)

# try-except文を使って、Ctrl+C でプログラムを終了することができるようにする
try: 
    # LED を点灯 (照度センサの値によって色を変更)
    led_on_illuminance(ser)

    # 60秒たったらLEDを消灯して終了
    time.sleep(60) 
    led_off(ser)

    # シリアルポートをクローズしてプログラムを終了
    ser.close()
    sys.exit(0)

except KeyboardInterrupt:
    # LED を消灯
    led_off(ser)

    # シリアルポートをクローズ
    ser.close()
