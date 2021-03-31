import os
import time
import tqdm
import datetime as dt
import pandas as pd
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool

_DIR_ = os.path.dirname(os.path.abspath(__file__))


def download_statusinvest():
    url = 'https://statusinvest.com.br/category/advancedsearchresultexport'
    params = {
        'search': '{}',
        'CategoryType': 1
    }

    res = requests.get(url, params=params)

    now = dt.datetime.now(tz=dt.timezone.utc)

    filename = f'{_DIR_}/data/statusinvest/statusinvest_{now.strftime("%Y-%m-%d_%H%M%S")}.csv'
    with open(filename, 'w') as f:
        lines = (res.content.decode()
                 .replace('.', '')
                 .replace(',', '.')
                 .replace(';', ',').split('\n'))

        lines[0] = f'{lines[0][:-1]},SETOR\n'
        f.write(lines[0])
        tickers = [lines[i].split(',')[0] for i in range(1, len(lines))]

        setores = []
        with Pool() as pool:
            for res in tqdm.tqdm(pool.imap_unordered(get_sector, tickers), total=len(tickers)):
                setores.append(res)

        setores = dict(setores)

        for i in range(1, len(lines)):
            ticker = lines[i].split(',')[0]
            lines[i] = f'{lines[i][:-1]},{setores[ticker]}\n'
            f.write(lines[i])

        # f.writelines(lines)


def get_sector(ticker):
    res = requests.get(f'https://statusinvest.com.br/acoes/{ticker}')
    soup = BeautifulSoup(res.content.decode(), features="lxml")
    try:
        setor = soup.find(text='Setor de Atuação').parent.find_next_sibling(
            'div').find('strong').text.upper()
    except AttributeError:
        print(f'ticker: {ticker} with sector None')
        setor = None
    return (ticker, setor)


def download_yahoofinance():
    files = os.listdir(f'{_DIR_}/data/statusinvest')

    if not any([f.startswith('statusinvest') for f in files]):
        raise ValueError('download statusinvest first')

    else:
        recent = sorted(files)[-1]
        filepath = f'{_DIR_}/data/statusinvest/{recent}'
        df = pd.read_csv(filepath)

        processes = []
        for ticker in tqdm.tqdm(df['TICKER']):
            yahoo_info_to_csv(ticker)


def yahoo_info_to_csv(ticker):
    get_url = 'https://query1.finance.yahoo.com/v7/finance/download/{}.SA'.format

    end = dt.datetime.now(tz=dt.timezone.utc)
    start = end - dt.timedelta(days=180)

    url = get_url(ticker)
    params = {
        'period1': int(start.timestamp()),
        'period2': int(end.timestamp()),
        'interval': '1d',
        'events': 'history',
        'includeAdjustedClose': True
    }

    res = requests.get(url, params=params)

    if res.status_code != 200:
        if res.status_code == 404:
            return
        else:
            print(ticker, res.status_code)
            while res.status_code == 401:
                time.sleep(60)
                res = requests.get(url, params=params)

    content = res.content.decode()

    filename = f'{_DIR_}/data/yahoofinance/{ticker}_{start.strftime("%Y-%m-%d")}_{end.strftime("%Y-%m-%d")}.csv'
    with open(filename, 'w') as f:
        f.write(content)


if __name__ == '__main__':
    dirs = [
        f'{_DIR_}/data/yahoofinance/',
        f'{_DIR_}/data/statusinvest/'
    ]
    for d in dirs:
        if not os.path.isdir(d):
            os.makedirs(d)

    download_statusinvest()
    download_yahoofinance()
