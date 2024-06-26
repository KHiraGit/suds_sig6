# 埼玉大学データサイエンス技術研究会 
# 第6回研究会 (2024/6/28) サンプルコード
# 作成者: 平松 薫
#
# 05_latestWacc2csv.py: 最新のセンサデータを取得し、CSVファイルに保存するプログラム #
# 
# 使い方: python 05_latestWacc2csv.py
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

# データの記録間隔
INTERVAL = 60

# CSVファイルを保存するフォルダ
OUTPUT_FOLDER = 'csv_files'

# CSVファイルのファイル名 (data2csv関数で、センサーデータ全部の場合、加速度データの場合のファイル名を追加)
_output_file_head = os.path.join(OUTPUT_FOLDER + '/' + 'iot_2jciebu_all_' + SERIAL_PORT)


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
        print("Invalid Header", ret)
        ret = b''
    elif ret[4] != 1 and ret[4] != 2:
        for i in range(len(ret)):
            print(f'({i}) {ret[i]:02x}', end=' ')
        print()
        print("Error Response", hex(ret[4]))
        ret = b''

    _ser.reset_input_buffer()
    _ser.reset_output_buffer()

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
        # retval = {"time_measured": datetime.now()} | retval # python 3.9 以降
        retval = {**{"time_measured": datetime.now()}, **retval}  # python 3.8 以前も含めた書き方
        return [retval]
    else:
        return None

def setup_sensor(_ser):
    """加速度データの記録を開始するため、timecounter をリセットする関数"""
    payload = bytearray([0x01, # Read 0x01, Write 0x02
                        0x02, 0x52, # Time setting (Address: 0x5202 をリトルエンディアンで送信)
                        ])
    ret = serial_read(_ser, payload)
    current_timecounter  = int.from_bytes(ret[7:15], 'little')
    print('current_timecounter (r)', current_timecounter)
    if current_timecounter == 0:
        payload = bytearray([0x02, # Read 0x01, Write 0x02
                            0x02, 0x52 # Time setting (Address: 0x5202 をリトルエンディアンで送信)
                            ]) + pack('<Q', 1) # UInt64 で 1 送信
        ret = serial_read(_ser, payload)
        current_timecounter  = int.from_bytes(ret[7:15], 'little')
        print('current_timecounter (w)', current_timecounter)

    payload = bytearray([0x01, # Read 0x01, Write 0x02
                        0x03, 0x52, # Memory storage interval (Address: 0x5203 をリトルエンディアンで送信)
                        ])
    ret = serial_read(_ser, payload)
    storage_interval  = int.from_bytes(ret[7:9], 'little')
    print('storage_interval (r)', storage_interval)
    if storage_interval < 3600:
        payload = bytearray([0x02, # Read 0x01, Write 0x02
                            0x03, 0x52 # Memory storage interval (Address: 0x5203 をリトルエンディアンで送信)
                            ]) + pack('<H', 3600) # UInt16 で 3600 送信
        ret = serial_read(_ser, payload)
        storage_interval  = int.from_bytes(ret[7:9], 'little')
        print('storage_interval (w)', storage_interval)

def read_acc_data_pages(_acc_data, _page, _time):
    # print(len(_acc_data))
    retval = []
    for i in range(0, len(_acc_data)-1, 6):
        if i+5 >= len(_acc_data):
            break
        x = s16(_acc_data[i+1] << 8 | _acc_data[i]) * 0.1
        y = s16(_acc_data[i+3] << 8 | _acc_data[i+2]) * 0.1
        z = s16(_acc_data[i+5] << 8 | _acc_data[i+4]) * 0.1
        # _timestamp = _time + (_page*32+i/6) * 0.01
        _timestamp = datetime.fromtimestamp(_time + (_page*32+i/6) * 0.01)
        # print(f'{_page} {i/6} x={x:.2f} y={y:.2f} z={z:.2f}', _timestamp, datetime.fromtimestamp(_timestamp), _timestamp)
        retval.append({"time_measured": _timestamp, 'acc_x': x, 'acc_y': y, 'acc_z': z})
    return retval

# CSVファイルを保存するフォルダを作成
output_folder = OUTPUT_FOLDER
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# センサデータをCSVファイルに保存するための関数
def data2csv(_data, _output_file_head):
    # 出力するデータが気温等か加速度データかを判定し、ファイル名を設定
    if len(_data) == 0:
        return
    elif 'temperature' in _data[0].keys():
        _output_file = _output_file_head + '.csv'
    else: # 加速度データの場合
        _output_file = _output_file_head + '_acc' + datetime.now().strftime('%Y%m%d%H%M%S') + '.csv'

    # _dataのキーをCSVのヘッダーとして出力
    if not os.path.exists(_output_file):
        _header = ''
        for key in _data[0].keys():
            if len(_header) == 0:
                _header = key
            else:
                _header = _header + ',' + key
        with open(_output_file, 'a') as f:
            f.write(_header + '\n')

    # _dataの値をCSVファイルに出力
    with open(_output_file, 'a') as f:
        for _row in _data:
            _output = ''
            for key in _row.keys():
                if len(_output) == 0:
                    _output = str(_row[key])
                else:
                    _output = _output + ',' + str(_row[key])
            f.write(_output + '\n')

    return

# シリアルポートをオープン
ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, serial.EIGHTBITS, serial.PARITY_NONE, write_timeout=1, timeout=1)

# センサの初期設定(加速度データの記録を開始するために timecounter をリセット)
setup_sensor(ser)

# センサの初期設定完了後、一度、センサからデータを取得して表示
ret = None
while ret is None:
    ret = get_current_data(ser)
    time.sleep(1)
print('# start sensing data', datetime.now(), ret)

# 地震・振動によって記録された加速度データを確認し、InfluxDBに格納するためのフラグ
earthquake_flag = False
vibration_flag = False
vibration_start_time = 0
vibration_end_time = 0
vibration_start_datetime = datetime.now().timestamp()

# try-except文を使って、Ctrl+C でプログラムを終了することができるように設定
try: 
    i = 0
    # while ser.isOpen() and i < 10:
    while ser.isOpen():
        # 最新センサデータを取得
        ret = get_current_data(ser)
        if ret is None:
            continue

        # カウンター(i)を確認し、INTERVAL で設定した間隔でデータをCSVファイルに保存
        if i % INTERVAL == 0:
            data2csv(ret, _output_file_head)

        if vibration_flag == False and ret[0]["vibration_information"] != 0:
            data2csv(ret, _output_file_head)
            vibration_flag = True
            vibration_start_time = ret[0]["time_measured"]
            vibration_start_timestamp = datetime.now().timestamp()
            if ret[0]["vibration_information"] == 2:
                print("### Earthquake detected", f'({ret[0]["time_measured"]})')
                earthquake_flag = True
            else:
                print("### vibration detected", f'({ret[0]["time_measured"]})')


        if vibration_flag == True and ret[0]["vibration_information"] == 0:
            data2csv(ret, _output_file_head)
            # Read the current timecounter
            payload = bytearray([0x01, # Read 0x01, Write 0x02
                                0x01, 0x52, # Latest time counter (Address: 0x5201 をリトルエンディアンで送信)
                                ])
            ret = serial_read(ser, payload)
            current_timecounter = int.from_bytes(ret[7:15], 'little')
            print(f'current_timecounter: {current_timecounter} (0x{current_timecounter:016x})')
            print(f'({i})', ret[0])

            if earthquake_flag:
                # Read the accelleration memory header.
                payload = bytearray([0x01, # Read 0x01, Write 0x02
                                    0x3E, 0x50, # Acceleration memory data [Header] (Address: 0x503E をリトルエンディアンで送信)
                                    0x00, # Acceleration data type 0x00: Earthquake data (Normal mode) 0x01: Vibration data (Normal mode)
                                    0x01, # Request acceleration memory index (Range: 0x01 to 0x0A (1 to 10) *0x01: Latest data <---> 0x0A: Last data)
                                    ])
                ret = serial_read(ser, payload)
                data_timecounter = int.from_bytes(ret[13:21], 'little')
                print(f'Earthquake end timecounter: {data_timecounter} (0x{data_timecounter:016x})')

                if data_timecounter != 0:
                    # Calculate time of vibration end.
                    vibration_end_time = vibration_start_datetime + (current_timecounter - data_timecounter)
                    print('current_timecounter', current_timecounter, 'data_timecounter', data_timecounter, 'diff', (current_timecounter - data_timecounter))
                    print(f'vibration_start_time: {vibration_start_time}') # ({datetime.fromtimestamp(vibration_start_time)})')
                    print(f'vibration_end_time: {vibration_end_time} ({datetime.fromtimestamp(vibration_end_time)})')

                    _start_page = 0x0001
                    _end_page = ret[7] | ret[8]<<8            
                    _payload = bytearray([0x01, # Read 0x01, Write 0x02
                                        0x3F, 0x50, # Acceleration memory data [Data] (Address: 0x503F)
                                        0x00, # Acceleration data type (0x00: Earthquake data 0x01: Vibration data)
                                        0x01, # Request acceleration memory index UInt8 0x01: Fixed value
                                        0x01, 0x00, # Request page (Start page)
                                        ret[7], ret[8]]) # Request page (End page)
                                        # ])+ pack('<H', _end_page - 1) # Request page (End page)
                    ret = serial_read(ser, _payload, timeout=1.0)
                    acc_data = []
                    for i in range(_end_page):
                        acc_data = acc_data + read_acc_data_pages(ret[i*237+43:(i+1)*237-2], i, vibration_start_timestamp)
                    data2csv(acc_data, _output_file_head)

                earthquake_flag = False

            else:
                # Read the accelleration memory header.
                payload = bytearray([0x01, # Read 0x01, Write 0x02
                                    0x3E, 0x50, # Acceleration memory data [Header] (Address: 0x503E をリトルエンディアンで送信)
                                    0x01, # Acceleration data type 0x00: Earthquake data (Normal mode) 0x01: Vibration data (Normal mode)
                                    0x01, # Request acceleration memory index (Range: 0x01 to 0x0A (1 to 10) *0x01: Latest data <---> 0x0A: Last data)
                                    ])
                ret = serial_read(ser, payload)
                data_timecounter = int.from_bytes(ret[13:21], 'little')
                print(f'Vibration end timecounter: {data_timecounter} (0x{data_timecounter:016x})')

                if data_timecounter != 0:
                    # Calculate time of vibration end.
                    vibration_end_time = vibration_start_datetime + (current_timecounter - data_timecounter)
                    print('current_timecounter', current_timecounter, 'data_timecounter', data_timecounter, 'diff', (current_timecounter - data_timecounter))
                    print(f'vibration_start_time: {vibration_start_time}') # ({datetime.fromtimestamp(vibration_start_time)})')
                    print(f'vibration_end_time: {vibration_end_time} ({datetime.fromtimestamp(vibration_end_time)})')
                    print()

                    _start_page = 0x0001
                    _end_page = ret[7] | ret[8]<<8            
                    _payload = bytearray([0x01, # Read 0x01, Write 0x02
                                        0x3F, 0x50, # Acceleration memory data [Data] (Address: 0x503F)
                                        0x01, # Acceleration data type (0x00: Earthquake data 0x01: Vibration data)
                                        0x01, # Request acceleration memory index UInt8 0x01: Fixed value
                                        0x01, 0x00, # Request page (Start page)
                                        ret[7], ret[8]]) # Request page (End page)
                                        # ])+ pack('<H', _end_page - 1) # Request page (End page)
                    ret = serial_read(ser, _payload, timeout=1.0)
                    acc_data = []
                    for i in range(_end_page):
                        acc_data = acc_data + read_acc_data_pages(ret[i*237+43:(i+1)*237-2], i, vibration_start_timestamp)
                    data2csv(acc_data, _output_file_head)

            vibration_flag = False

        time.sleep(1) # 1秒スリープ
        i = i + 1

except KeyboardInterrupt:
    # シリアルポートをクローズ
    ser.close()
