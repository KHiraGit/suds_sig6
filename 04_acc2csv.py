# 埼玉大学データサイエンス技術研究会 
# 第6回研究会 (2024/6/28) サンプルコード
# 作成者: 平松 薫
#
# 04_acc2csv.py: 最新の加速度データを取得してCSVファイルに保存するプログラム #
# 
# 使い方: python 04_acc2csv.py
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

# CSVファイルを保存するフォルダを作成
output_folder = 'csv_files'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# CSVファイルのファイル名
_output_file = os.path.join(output_folder + '/' + 'iot_2jciebu_acc_' + SERIAL_PORT + '.csv')

# try-except文を使って、Ctrl+C でプログラムを終了することができるようにする
try: 
    print("Start recording accelaration sensor data: ", _output_file)
    print("Press Ctrl+C to stop recording (max 100 samples)")

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

        # 時刻を取得
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        if not os.path.exists(_output_file):
            # _data_dictのキーをCSVのヘッダーとして出力
            _header = 'timestamp, x, y, z'
        else:
            _header = ''
        _output = f'{timestamp},{x},{y},{x}'

        with open(_output_file, 'a') as f:
            if len(_header) > 0:
                f.write(_header + '\n')
            f.write(_output + '\n')

        # print(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), f"x={x:.2f}, y={y:.2f}, z={z:.2f}")
        time.sleep(0.1)
        i += 1

except KeyboardInterrupt:
    # シリアルポートをクローズ
    ser.close()
