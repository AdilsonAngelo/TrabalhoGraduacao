import time
import datetime as dt
import requests
from playwright import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd


def get_top5() -> pd.DataFrame:
    with sync_playwright() as playwright:
        res = run(playwright)
    return res[-1].loc[:4]


def run(playwright):
    headless = True
    # headless = False
    browser = playwright.chromium.launch(headless=headless)
    context = browser.newContext()

    # Open new page
    page = context.newPage()

    # Go to https://www.moneytimes.com.br/tag/carteira-recomendada/
    page.goto("https://www.moneytimes.com.br/tag/carteira-recomendada/",
              waitUntil='domcontentloaded')

    for i in range(10):
        time.sleep(1)
        page.keyboard.press('PageDown')
        soup = BeautifulSoup(page.innerHTML('body'))
        urls = get_relevant_urls(soup)
        if len(urls) > 0:
            break

    # Close page
    page.close()

    # ---------------------
    context.close()
    browser.close()

    soup = BeautifulSoup(requests.get(urls[0]).text)

    return get_tables_from_html(soup)


def get_relevant_urls(soup: BeautifulSoup):
    return [s.find('a')['href'] for s in soup.find_all(class_='news-item__title')
            if s.find('a').get_text().startswith('Dividendos:')
            and has_current_month(s.find('a').get_text())]


def get_tables_from_html(soup: BeautifulSoup):

    dfs = []
    for table in soup.find_all('table'):
        table_headers = [th.text for th in table.find_all('th')]
        table_data = [th.text for th in table.find_all('td')]
        table_rows = [table_data[i:i+len(table_headers)]
                      for i in range(0, len(table_data), len(table_headers))]

        dfs.append(pd.DataFrame(table_rows, columns=table_headers))
    return dfs


def has_current_month(s: str):
    map_months = {
        1: 'janeiro',
        2: 'fevereiro',
        3: 'março',
        4: 'abril',
        5: 'maio',
        6: 'junho',
        7: 'julho',
        8: 'agosto',
        9: 'setembro',
        10: 'outubro',
        11: 'novembro',
        12: 'dezembro'
    }
    current_month = map_months[dt.datetime.now().month]

    return current_month in s.lower()


print(get_top5())
