import requests
from bs4 import BeautifulSoup

url = "https://fundamentus.com.br/detalhes.php"


payload = ""
headers = {
    'cookie': "__cfduid=d84796ca16170a58f296efed0cf24514a1611513340; PHPSESSID=1044771291df37ab455394de9468bf58; __utmc=138951332; __utmz=138951332.1611513342.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); _qn=1; __utma=138951332.1388485926.1611513342.1613935152.1613937167.8; __utmt=1; __cf_bm=371a925b55141fc066db8b9094462ebb88bc95cd-1613937167-1800-ASEXqmIY6lwBXCJYhwc6nhoPzGDhpgbwUSJOO+lMPDmxXUfvzKwp0s4AplpXvLl+fjlBLq9K39kO+eycZLUQL9y+jtP3k0kzPoxQfOt1Aq4aNBlYf6u8iPyGMzqaBM6YSA==; __utmb=138951332.4.10.1613937167",
    'authority': "fundamentus.com.br",
    'cache-control': "max-age=0",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    'sec-fetch-site': "none",
    'sec-fetch-mode': "navigate",
    'sec-fetch-user': "?1",
    'sec-fetch-dest': "document",
    'accept-language': "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
}


def deepest(root, tag):
    descendant = root.find(tag)
    if descendant:
        return deepest(descendant, tag)
    return root


def br_to_us_num(num):
    print(num)
    if num.strip() == '-':
        num = '0'
    return float(num.replace('.', '').replace(',', '.').strip())


def get_missing_data(ticker: str, missing: [str]):

    map_fields = {
        'CAGR RECEITAS 5 ANOS': 'Cres. Rec (5a)',
        'ROIC': 'ROIC',
        'LIQ CORRENTE': 'Liquidez Corr',
        'P/CAP GIRO': 'P/Cap. Giro',
        'PSR': 'PSR',
    }

    querystring = {"papel": ticker}
    response = requests.get(url,
                            data=payload,
                            headers=headers,
                            params=querystring)

    soup = BeautifulSoup(response.text)

    ziped = list(zip(soup.find_all('td', 'label'),
                     soup.find_all('td', 'data')))

    res = dict()
    for m in missing:
        if m == 'DIV LIQ/PATRI':
            div_liq, pat_liq = None, None
            for z in ziped:
                if z[0].find(text='Dív. Líquida'):
                    div_liq = br_to_us_num(deepest(z[1], 'span').text)
                elif z[0].find(text='Patrim. Líq'):
                    pat_liq = br_to_us_num(deepest(z[1], 'span').text)
            if div_liq is None or pat_liq is None:
                continue
            res[m] = div_liq/pat_liq
        else:
            for z in ziped:
                if z[0].find(text=map_fields[m]):
                    res[m] = br_to_us_num(deepest(z[1], 'span').text)
                    break

    return res


print(get_missing_data('ITSA4', ['PSR', 'DIV LIQ/PATRI']))
