# 埼玉大学データサイエンス技術研究会 
# 第6回研究会 (2024/6/28) サンプルコード
# Description: CSV形式で保存したセンサーデータの統計情報を表示する
# Author: Kaoru Hiramatsu, Saitama Univ.
# Created: 2024/06/26
# Last modified: 2024/06/27
# 
# 使い方: python 21_csv2stat.py (CSVファイル名)
#

import pandas as pd
import sys
import os

args = sys.argv

if not os.path.exists(args[1]):
    print("指定されたファイルが見つかりません", args[1])
    sys.exit()
elif not args[1].endswith(".csv"):
    print("CSVファイルを指定してください")
    sys.exit()
else:
    # CSV形式で保存したセンサーデータをデータフレームに読み込む（index_col=0で1列目をインデックスに指定）
    df = pd.read_csv(args[1], index_col=0)

    # 読み込んだデータの統計情報を表示
    for column in df.columns:
        if column not in ['timestamp', 'data_mode', 'sequence_number']:
            print('\n##', column)
            print(df[column].describe())
