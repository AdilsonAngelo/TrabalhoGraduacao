import pandas as pd
import os

_DIR = os.path.dirname(os.path.abspath(__file__))

data_frame = pd.read_csv(_DIR + '/X.csv', index_col='TICKER')