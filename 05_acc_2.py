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
        raise print("Invalid Header", ret)
    if ret[4] != 0 and ret[4] != 1:
        raise print("Error Response", hex(ret[4]))
    return ret

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

def led_on(_ser):
    """
    LEDを点灯する関数
    """
    _payload = bytearray([0x02, # Read 0x01, Write 0x02
                          0x11, 0x51, # LED設定 (0x5111 をリトルエンディアンで送信)
                          0x01, 0x00, # LEDを点灯 (0x0001 をリトルエンディアンで送信)
                          0xFF, 0xFF, 0xFF]) # 色設定　RGB ここでは赤に設定
    serial_write(_ser, _payload)

def logging_start(_ser):
    # 加速度データの記録を開始
    payload = bytearray([0x02, # Read 0x01, Write 0x02
                        0x18, 0x51, # Acceleration logger control (0x5118 をリトルエンディアンで送信)
                        0x01, # 0x00: Log stop 0x01: Log start
                        0x00, # Range of detection (固定値)
                        0x03, # ODR setting (0x00: 1 Hz 0x02: 25 Hz 0x03: 100 Hz 0x04: 200 Hz 0x05: 400 Hz)
                        0x01, 0x00, # Start page (range 0x0001 to 0x2800 (0x0001 をリトルエンディアンで送信))
                        0x10, 0x00]) # End page (0x0010 をリトルエンディアンで送信)
    ret = serial_write(_ser, payload)
    time.sleep(0.1)
    ret = _ser.read(_ser.inWaiting())
    print('### Acceleration data logging start ###', datetime.now().strftime("%Y-%m-%d %H:%M:%S %f"))
    return

def logging_stop(_ser):
    # 加速度データの記録を終了
    payload = bytearray([0x02, # Read 0x01, Write 0x02
                        0x18, 0x51, # Acceleration logger control (0x5118 をリトルエンディアンで送信)
                        0x00, # 0x00: Log stop 0x01: Log start
                        0x00, # Range of detection (固定値)
                        0x03, # ODR setting (0x00: 1 Hz 0x02: 25 Hz 0x03: 100 Hz 0x04: 200 Hz 0x05: 400 Hz)
                        0x01, 0x00, # Start page (range 0x0001 to 0x2800 (0x0001 をリトルエンディアンで送信))
                        0x10, 0x00]) # End page (0x0010 をリトルエンディアンで送信)
    ret = serial_write(_ser, payload)
    time.sleep(0.1)
    ret = _ser.read(_ser.inWaiting())
    print('### Acceleration data logging stop ###', datetime.now().strftime("%Y-%m-%d %H:%M:%S %f"))
    return

# シリアルポートをオープン (インストール状況・実行環境に応じて COM3 を変更)
ser = serial.Serial("COM4", 115200, serial.EIGHTBITS, serial.PARITY_NONE)

led_on(ser)
# payload = bytearray([0x01, # Read 0x01, Write 0x02
#                      0x17, 0x51, # Mode change (0x5117 をリトルエンディアンで送信)
#                      0x01]) # 0x00: Normal mode (default) 0x01: Acceleration logger mode
# ret = serial_read(ser, payload) # モード切替時にフラッシュメモリが消去されるため、約2分かかる
command = bytearray([0x52, 0x42, # Header
                    0x06, 0x00, # Length
                    0x01, # Read 0x01, Write 0x02
                    0x17, 0x51,
                    0x01])
command = command + calc_crc(command, len(command))
ser.write(command)
time.sleep(0.1)
ret = ser.read(ser.inWaiting())
led_off(ser)

logging_start(ser)

# try-except文を使って、Ctrl+C でプログラムを終了することができるようにする
try: 
    i = 0
    while i < 10:
        time.sleep(1)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S %f"))

        command = bytearray([0x52, 0x42, # Header
                            0x05, 0x00, # Length
                            0x01, # Read 0x01, Write 0x02
                            0x19, 0x51]) # Acceleration logger status (0x5119 をリトルエンディアンで送信)
        command = command + calc_crc(command, len(command))
        ser.write(command)
        time.sleep(0.1)
        ret = ser.read(ser.inWaiting())
        for j in range(len(ret)):
            print(j, f'{ret[j]:02x}', end=' ')
        print()

        # # 最新データを取得
        # payload = bytearray([0x01, # Read 0x01, Write 0x02
        #                      0x21, 0x50]) # Latest data long (0x5021 をリトルエンディアンで送信)
        # ret = serial_read(ser, payload)
        # print(ret)

        # 最新の time counter を取得
        # payload = bytearray([0x01, # Read 0x01, Write 0x02
        #                      0x19, 0x51]) # Acceleration logger status (0x5119 をリトルエンディアンで送信)
        # ret = serial_read(ser, payload)
        # print(ret)

        # 最新の time counter を取得
        # payload = bytearray([0x01, # Read 0x01, Write 0x02
        #                      0x01, 0x52]) # Latest time counter (0x5201 をリトルエンディアンで送信)
        # ret = serial_read(ser, payload)
        # print(ret)

        i = i + 1
    logging_stop(ser)
    # シリアルポートをクローズ
    ser.close()

except KeyboardInterrupt:
    logging_stop(ser)
    # シリアルポートをクローズ
    ser.close()

