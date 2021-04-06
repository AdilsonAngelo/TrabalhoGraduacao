import pandas as pd
import os

_DIR = os.path.dirname(os.path.abspath(__file__))

data_frame = pd.read_csv(_DIR + '/X.csv', index_col='TICKER')

names = pd.read_csv(_DIR + '/nomes.csv', index_col='TICKER')

greenblatt = pd.Series([i for i in range(len(data_frame))],
                      index=data_frame.sort_values(by=['ROE'], ascending=True).index) + \
            pd.Series([i for i in range(len(data_frame))],
                      index=data_frame.sort_values(by=['P/L'], ascending=False).index)

greenblatt = (greenblatt - greenblatt.min()) / (greenblatt.max() - greenblatt.min())