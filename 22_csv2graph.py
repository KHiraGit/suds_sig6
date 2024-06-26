# 埼玉大学データサイエンス技術研究会 
# 第6回研究会 (2024/6/28) サンプルコード
# Description: CSV形式で保存したセンサーデータのグラフを表示 （ブラウザを起動して表示）
# Author: Kaoru Hiramatsu, Saitama Univ.
# Created: 2024/06/26
# Last modified: 2024/06/26

import pandas as pd
import sys
import os
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

    # 読み込んだデータの観測値をリストに格納
    graph_data = []
    for column in df.columns:
        if column not in ['timestamp', 'data_mode', 'sequence_number']:
            graph_data.append(column)

    # グラフの初期化 (複数のグラフを縦に並べて表示する)
    fig = make_subplots(rows=len(graph_data), cols=1, subplot_titles=graph_data, 
                        shared_xaxes='all', 
                        vertical_spacing=0.01)

    # グラフを表示
    for i in range(len(graph_data)):
        fig.add_trace(go.Scatter(x=df.index, y=df[graph_data[i]], mode='lines', name=graph_data[i]), row=i+1, col=1)

    # グラフが1つの時は、レンジスライダーを表示すると表示範囲の指定が容易
    # fig.update_xaxes(rangeslider_visible=True)

    fig.update_layout(title='Omron Sensor Data', 
                    #   xaxis_title='Time', 
                    yaxis_title='Sensor Data',
                    showlegend=True,
                    width=1000,
                    height=400*len(graph_data),
                    )
    
    fig.show()
