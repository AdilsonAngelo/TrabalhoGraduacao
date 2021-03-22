from io import StringIO
import datetime as dt
import requests
import pandas as pd
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def get_data(ticker, start: dt.datetime, end: dt.datetime):
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}.SA"

    start = int(start.timestamp())
    end = int(end.timestamp())

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
    return df


def get_last_close(ticker):
    now = dt.datetime.now()
    start = now - dt.timedelta(days=7)
    df = get_data(ticker, start, now)
    return df.iloc[-1]['Adj Close']


def get_day_variation(ticker):
    now = dt.datetime.now()
    start = now - dt.timedelta(days=7)
    df = get_data(ticker, start, now)
    var = df.iloc[-1]['Adj Close'] / df.iloc[-2]['Adj Close']
    return var


def top_variations():
    res = requests.get('https://statusinvest.com.br')
    soup = BeautifulSoup(res.text, features="lxml")
    top_vars = dict()

    def get_altas_baixas(tipo):
        res = {'empresa': [], 'variação': []}
        for link in soup.find('h3', text=tipo).parent.find_all('a'):
            if 'see-all' in link['class']:
                continue
            link.find('small').extract()
            link.find('i').extract()
            res['empresa'].append(link.find('h4').get_text().strip())
            res['variação'].append(link.find('span', 'value')
                                   .get_text()
                                   .replace('.', '')
                                   .replace(',', '.'))
        return res

    top_vars['baixas'] = pd.DataFrame(get_altas_baixas('BAIXAS'))
    top_vars['altas'] = pd.DataFrame(get_altas_baixas('ALTAS'))

    return top_vars
