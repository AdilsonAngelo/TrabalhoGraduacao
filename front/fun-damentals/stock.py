from io import StringIO
import datetime as dt
import requests
import pandas as pd
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def get_last_close(ticker):
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}.SA"

    now = dt.datetime.now()

    start = int((now - dt.timedelta(days=7)).timestamp())
    end = int(now.timestamp())

    querystring = {
        "period1": start,
        "period2": end,
        "interval": "1d",
        "events": "history",
        "includeAdjustedClose": "true"
    }

    headers = {"cookie": "B=007fk1tg0rhli%26b%3D3%26s%3D50"}

    response = requests.get(url, headers=headers, params=querystring)
    
    df = pd.read_csv(StringIO(response.text))

    return df.iloc[-1]['Adj Close']
