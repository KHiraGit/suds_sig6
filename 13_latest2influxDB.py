# 埼玉大学データサイエンス技術研究会 
# 第6回研究会 (2024/6/14) サンプルコード
# 作成者: 平松 薫
#
# 13_latest.py: 最新のセンサデータを取得し、データベースに格納するプログラム #
# 
# 使い方: python 13_latest.py
#

import os
import sys
import time
from datetime import datetime
from struct import pack, unpack
import serial
import influxdb
import influxdb_client, time
from influxdb_client import Point
from influxdb_client.client.write_api import WriteOptions


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
    # time.sleep(0.1)
    return

def serial_read(_ser, _payload, timeout=0.0):
    """
    環境センサにコマンドを送信し、レスポンスを取得する関数
    _payload の前にヘッダと_payloadの長さを付加、後に CRC-16 を付加して送信
    レスポンスはシリアルポートから読み込み、そのまま返す
    """
    if len(_payload) > 0:
        serial_write(_ser, _payload)
    else:
        return b''

    ret = b''
    command_head_len = 4
    i = 0
    while True:
        _ser_len = _ser.inWaiting()
        if _ser_len > 0:
            ret += _ser.read(_ser_len)
            if _ser_len > 3 and len(ret) >= (ret[2] | (ret[3] << 8)) + command_head_len:
                break
        else:
            i = i + 1
            if i >= 10:
                print('serial port timeout')
                return b''
            time.sleep(0.1)

    if ret[0:2] != b'\x52\x42':
        raise print("Invalid Header", ret)
    if ret[4] != 1 and ret[4] != 2:
        for i in range(len(ret)):
            print(f'({i}) {ret[i]:02x}', end=' ')
        print()
        raise print("Error Response", hex(ret[4]))
    return ret

def dump_data(_ret):
    for i in range(len(_ret)):
        print(f'({i}) {_ret[i]:02x}', end=' ')
        if i % 16 == 15:
            print()
    print()
    return

fields = ["temperature", "relative_humidity", "ambient_light",
          "barometric_pressure", "sound_noise", "eTVOC", "eCO2",
          "discomfort_index", "heat_stroke", "vibration_information",
          "si_value", "pga", "seismic_intensity"]

def get_current_data(_ser):
    # Read the latest sensor data.
    payload = bytearray([0x01, # Read 0x01, Write 0x02
                        0x21, 0x50, # Latest data Long (Address: 0x5021 をリトルエンディアンで送信)
                        ])
    ret = serial_read(_ser, payload)
    if len(ret) > 0:
        values = unpack('<hHHLHHHHhBHHH', ret[8:35])
        units = [0.01, 0.01, 1, 0.001, 0.01, 1, 1, 0.01, 0.01, 1, 0.1, 0.1, 0.001]
        retval = dict([ [k, v * u] for k, v, u in zip(fields, values, units)])
        retval["time_measured"] = datetime.now()
        return retval
    else:
        return None

# シリアルポートをオープン (インストール状況・実行環境に応じて COM3 を変更)
ser = serial.Serial("COM4", 115200, serial.EIGHTBITS, serial.PARITY_NONE)

# InfluxDB に接続
# url = "http://localhost:8086"
host = "192.168.11.81"
port = 8086
database ="sensor_2jcie_bu01_kh1"
username = "sensor"
password = "sensor_pw"

class Database:
    def __init__(self, _host, _port, _database, _username, _password):
        self.influx = influxdb.InfluxDBClient(host=_host, port=_port, database=_database, username=_username, password=_password)

    def write(self, data):
        _field_data = {}
        for key in data.keys():
            if key != "time_measured":
                _field_data[key] = data[key]

        json_body = [{
            'measurement': 'sensor',
            'tags': {'macaddr': ''},
            # 'time': data['time_measured'],
            'time': datetime.utcnow(),
            'fields': _field_data
        }]
        self.influx.write_points(json_body)

    def close(self):
        # self.write_api.close()
        # self.client.close()
        self.influx.close()

influxDB = Database(host, port, database, username, password)

# try-except文を使って、Ctrl+C でプログラムを終了することができるようにする
try: 
    i = 0
    # while ser.isOpen() and i < 10:
    while ser.isOpen():
        # 最新センサデータを取得
        ret = get_current_data(ser)
        if ret is not None:
            if i % 10 == 0:
                print(ret)
            influxDB.write(ret)
        # time.sleep(1)
        time.sleep(10) # 10秒ごとにデータを取得して InfluxDB に格納
        i = i + 1

except KeyboardInterrupt:
    # シリアルポートをクローズ
    ser.close()
    influxDB.close()
