import requests
import dash_html_components as html
import dash_bootstrap_components as dbc
from data.stocks import data_frame

__AVAILABLE_TICKERS = list(data_frame.index)


def validate_ticker(ticker: str):
    return ticker.upper() in __AVAILABLE_TICKERS


def render_not_found():
    return dbc.Alert(
        color='danger',
        children=html.H2('404: not found 😢')
    )
