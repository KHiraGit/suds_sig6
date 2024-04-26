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

def led_off(_ser):
    """
    LEDを消灯する関数
    """
    print('LED OFF')
    _payload = bytearray([0x02, # Read 0x01, Write 0x02
                          0x11, 0x51, # LED設定 (0x5111 をリトルエンディアンで送信)
                          0x00, 0x00, # LED常時消灯 (0x0000 をリトルエンディアンで送信)
                          0x00, 0x00, 0x00]) # 色設定　RGB ここでは赤に設定
    ret = serial_read(_ser, _payload)
    dump_data(ret)
    return

def led_on(_ser):
    """
    LEDを点灯する関数
    """
    print('LED ON')
    _payload = bytearray([0x02, # Read 0x01, Write 0x02
                          0x11, 0x51, # LED設定 (0x5111 をリトルエンディアンで送信)
                          0x01, 0x00, # LEDを点灯 (0x0001 をリトルエンディアンで送信)
                          0xFF, 0xFF, 0xFF]) # 色設定　RGB ここでは白に設定
    ret = serial_read(_ser, _payload)
    dump_data(ret)
    return

def logging_start(_ser):
    """
    加速度データの記録を開始
    """
    print('### Change mode to Acceleration data logging...')
    _payload = bytearray([0x01, # Read 0x01, Write 0x02
                        0x17, 0x51]) # 4 Mode change (Address: 0x5117 をリトルエンディアンで送信)
    ret = serial_read(_ser, _payload)
    dump_data(ret)
    # payload = bytearray([0x02, # Read 0x01, Write 0x02
    #                     0x17, 0x51, # 4 Mode change (Address: 0x5117 をリトルエンディアンで送信)
    #                     0x01]) # 0x00: Normal mode (default) 0x01: Acceleration logger mode
    # ret = serial_read(_ser, payload)
    # time.sleep(150)
    print('### Acceleration data logging start ###', end=' ')
    _payload = bytearray([0x02, # Read 0x01, Write 0x02
                        0x18, 0x51, # Acceleration logger control (0x5118 をリトルエンディアンで送信)
                        0x01, # 0x00: Log stop 0x01: Log start
                        0x00, # Range of detection (固定値)
                        0x03, # ODR setting (0x00: 1 Hz 0x02: 25 Hz 0x03: 100 Hz 0x04: 200 Hz 0x05: 400 Hz)
                        0x01, 0x00, # Start page (range 0x0001 to 0x2800 (0x0001 をリトルエンディアンで送信))
                        0x00, 0x28]) # End page (0x2800 をリトルエンディアンで送信)
    ret = serial_read(_ser, _payload)
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S %f"))
    dump_data(ret)
    return

def logging_stop(_ser):
    """
    加速度データの記録を終了
    """
    print('### Change mode to Acceleration data logging...')
    _payload = bytearray([0x02, # Read 0x01, Write 0x02
                        0x17, 0x51, # 4 Mode change (Address: 0x5117 をリトルエンディアンで送信)
                        0x00]) # 0x00: Normal mode (default) 0x01: Acceleration logger mode
    ret = serial_read(_ser, _payload)
    print('### Acceleration data logging stop ###', end=' ')
    _payload = bytearray([0x02, # Read 0x01, Write 0x02
                        0x18, 0x51, # Acceleration logger control (0x5118 をリトルエンディアンで送信)
                        0x00, # 0x00: Log stop 0x01: Log start
                        0x00, # Range of detection (固定値)
                        0x03, # ODR setting (0x00: 1 Hz 0x02: 25 Hz 0x03: 100 Hz 0x04: 200 Hz 0x05: 400 Hz)
                        0x01, 0x00, # Start page (range 0x0001 to 0x2800 (0x0001 をリトルエンディアンで送信))
                        0x00, 0x28]) # End page (0x2800 をリトルエンディアンで送信)
    ret = serial_read(_ser, _payload)
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S %f"))
    dump_data(ret)
    return

def check_logger_status(_ser):
    """
    ロガーの状態を確認する関数
    """
    print('### check_logger_status ###')
    _payload = bytearray([0x01, # Read 0x01, Write 0x02
                         0x19, 0x51]) # Acceleration logger status (Address: 0x5119 をリトルエンディアンで送信)
    ret = serial_read(_ser, _payload)
    dump_data(ret)
    return

def dump_data(_ret):
    for i in range(len(_ret)):
        print(f'({i}) {_ret[i]:02x}', end=' ')
    print()
    return

# シリアルポートをオープン
ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, serial.EIGHTBITS, serial.PARITY_NONE, write_timeout=1, timeout=1)
ser.reset_input_buffer()
ser.reset_output_buffer()

led_on(ser)

payload = bytearray([0x01, # Read 0x01, Write 0x02
                     0x02, 0x52, # Time setting (Address: 0x5202 をリトルエンディアンで送信)
                     ])
ret = serial_read(ser, payload)
current_timecounter  = int.from_bytes(ret[7:15], 'little')
print('current_timecounter (r)', current_timecounter)
if current_timecounter == 0:
    payload = bytearray([0x02, # Read 0x01, Write 0x02
                        0x02, 0x52 # Time setting (Address: 0x5202 をリトルエンディアンで送信)
                        ]) + pack('<Q', 1) # UInt64 で 1 送信
    ret = serial_read(ser, payload)
    current_timecounter  = int.from_bytes(ret[7:15], 'little')
    print('current_timecounter (w)', current_timecounter)

payload = bytearray([0x01, # Read 0x01, Write 0x02
                     0x03, 0x52, # Memory storage interval (Address: 0x5203 をリトルエンディアンで送信)
                     ])
ret = serial_read(ser, payload)
storage_interval  = int.from_bytes(ret[7:9], 'little')
print('storage_interval (r)', storage_interval)
if storage_interval < 3600:
    payload = bytearray([0x02, # Read 0x01, Write 0x02
                        0x03, 0x52 # Memory storage interval (Address: 0x5203 をリトルエンディアンで送信)
                        ]) + pack('<H', 300) # UInt16 で 3600 送信
    ret = serial_read(ser, payload)
    storage_interval  = int.from_bytes(ret[7:9], 'little')
    print('storage_interval (w)', storage_interval)
# time.sleep(150) # This process takes about 2min.

led_off(ser)

check_logger_status(ser)

logging_start(ser)

# try-except文を使って、Ctrl+C でプログラムを終了することができるようにする
try: 
    i = 0
    while i < 10:
        time.sleep(1)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S %f"))

        check_logger_status(ser)

        # command = bytearray([0x52, 0x42, # Header
        #                     0x05, 0x00, # Length
        #                     0x01, # Read 0x01, Write 0x02
        #                     0x19, 0x51]) # Acceleration logger status (0x5119 をリトルエンディアンで送信)
        # command = command + calc_crc(command, len(command))
        # ser.write(command)
        # time.sleep(0.1)
        # ret = ser.read(ser.inWaiting())
        # dump_data(ret)

        # # 最新データを取得
        # payload = bytearray([0x01, # Read 0x01, Write 0x02
        #                      0x21, 0x50]) # Latest data long (0x5021 をリトルエンディアンで送信)
        # ret = serial_read_2(ser, payload)
        # print(ret)

        # 最新の time counter を取得
        # payload = bytearray([0x01, # Read 0x01, Write 0x02
        #                      0x19, 0x51]) # Acceleration logger status (0x5119 をリトルエンディアンで送信)
        # ret = serial_read_2(ser, payload)
        # print(ret)

        # 最新の time counter を取得
        # payload = bytearray([0x01, # Read 0x01, Write 0x02
        #                      0x01, 0x52]) # Latest time counter (0x5201 をリトルエンディアンで送信)
        # ret = serial_read_2(ser, payload)
        # print(ret)

        i = i + 1
    logging_stop(ser)
    # シリアルポートをクローズ
    ser.close()

except KeyboardInterrupt:
    logging_stop(ser)
    # シリアルポートをクローズ
    ser.close()

