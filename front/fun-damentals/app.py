import string
import random
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import stock
import utils
import numpy as np
import locale
from data.stocks import data_frame, names, greenblatt
from recommendations import get_top5
from stock import top_variations

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

INITIAL_FEATURES = [
    'VALOR DE MERCADO',
    'DY',
    'LPA',
    'PSR',
    'MARGEM BRUTA',
    'ROE',
]


def to_percent_view(x): return f'{x:.2f}%'


view_modifiers = {
    'VALOR DE MERCADO': lambda x: locale.currency(x, grouping=True),
    'DY': to_percent_view,
    'MARGEM BRUTA': to_percent_view,
    'MARGEM EBIT': to_percent_view,
    'MARG LIQUIDA': to_percent_view,
    'ROE': to_percent_view,
    'ROA': to_percent_view,
    'ROIC': to_percent_view,
    'CAGR RECEITAS 5 ANOS': to_percent_view
}

app = dash.Dash(external_stylesheets=[dbc.themes.LUX],
                suppress_callback_exceptions=True)

app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    dbc.NavbarSimple(color='primary',
                     brand='FUNDAMENTALS',
                     dark=True,
                     children=[
                         dbc.NavItem(dbc.Select(
                             id='select',
                             placeholder='ITSA4',
                             options=list(
                                 map(lambda x: {'label': x, 'value': x}, list(data_frame.index))),
                         ))
                     ]),
    html.Div(id='page-content')
])


@app.callback(Output('url', 'pathname'),
              [Input("select", "value")])
def output_select(value):
    val = value if value is not None else ''

    return f'/{val}'


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):

    ticker = pathname.replace('/', '')

    if ticker == '':
        return render_welcome()

    # if not utils.validate_ticker(ticker):
    #     return utils.render_not_found()

    return render_stock_info(ticker.upper())


def card(title, text, color='secondary', outline=False):
    return dbc.Card(color=color, outline=outline, children=dbc.CardBody([
        html.H5(className='card-dash.dependenciestitle', children=title),
        html.Div(className='card-text', children=text)
    ]))


def render_stock_info(ticker: str):

    content = html.Div([
        dbc.Row([
            dbc.Col([
                html.H2(children=[html.B(f'{ticker} - '),
                                  html.Small(f'{names.loc[ticker]["NOME"]}')]),
                html.Small(f'{data_frame.loc[ticker]["SETOR"]}')
            ])
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Col(card(['Último fechamento', html.Hr()],
                         html.H2(
                             locale.currency(stock.get_last_close(
                                 ticker), grouping=True)
            ),
                'success'),
            ),
            dbc.Col(card(['Preço Justo',
                          html.Hr(),
                          html.A(html.Small('Fórmula de Benjamin Graham'),
                                 href='https://b7invest.com.br/2020/12/preco-justo-das-acoes-calculadora/')],
                         html.H2(locale.currency(
                             get_graham(data_frame.loc[ticker]), grouping=True))
                         )
                    ),
            dbc.Col(
                card(['Posição percentual',
                      html.Hr(),
                      html.A(html.Small('Fórmula de Joel Greenblatt'),
                             href='https://www.btgpactualdigital.com/blog/coluna-andre-bona/a-formula-magica-de-greenblatt-para-escolha-de-acoes')],
                     html.H2(f'{100*greenblatt.loc[ticker]:.0f}%',
                             style={
                                 'color': f'rgb({255*(1-greenblatt.loc[ticker])},100,{255*greenblatt.loc[ticker]})'
                             })
                     )
            )
        ]),
        html.Hr(),
        dbc.Spinner(html.Div(id="loading-output")),
        html.Div(id="second-output"),
        dbc.Row(
            dbc.Col(
                dbc.Button("Carregar mais", id="load-more-button",
                           color='info', className="mr-2", block=True)
            )
        )
    ])

    return content


@ app.callback(Output("loading-output", "children"),
               [Input('url', 'pathname')])
def load_rows(pathname):
    ticker = pathname.replace('/', '').upper()
    data = crunch_data(ticker, data_frame[INITIAL_FEATURES + ['SETOR']])

    return gen_rows(ticker, data)


@ app.callback(Output("second-output", "children"),
               [Input("load-more-button", "n_clicks"),
                Input('url', 'pathname')])
def load_more_rows(n_clicks, pathname):
    if n_clicks == 1:
        ticker = pathname.replace('/', '').upper()
        data = crunch_data(ticker, data_frame[[col
                                               for col in data_frame.columns
                                               if col not in INITIAL_FEATURES]])
        return gen_rows(ticker, data)


def progress_graph(ticker: str, series: pd.Series):
    _id = ''.join(random.choices(string.ascii_lowercase, k=5))

    return [
        dbc.Progress(id=_id, value=100, striped=True, bar_style={
                     'background': 'linear-gradient(90deg, rgba(255,100,0,1) 0%, rgba(0,100,255,1) 100%)'
                     }),
        dbc.Tooltip(ticker,
                    id=f'{_id}-tt',
                    target=_id,
                    offset='top+25%')
    ]


def simple_boxplot(ticker: str, series: pd.Series):
    fig = go.Figure()

    fig.add_trace(go.Box(x=series,
                         name='',
                         text=series.index,
                         jitter=.8,
                         pointpos=0,
                         opacity=1,
                         boxpoints='all',
                         width=1,
                         selectedpoints=[series.index.get_loc(ticker)],
                         selected=dict(marker=dict(
                             opacity=1, color='red', size=15)),
                         marker=dict(opacity=1),
                         line=dict(color='#072859')))
    fig.add_annotation(x=np.log10(series.loc[ticker]),
                       text=ticker,
                       showarrow=True,
                       arrowhead=1,
                       arrowcolor="red",
                       arrowsize=2,
                       arrowwidth=1)

    fig.update_layout(height=100,
                      margin=dict(l=20, r=20, t=20, b=20))

    return dcc.Graph(figure=fig)


def crunch_data(ticker: str, df: pd.DataFrame) -> dict:
    skip = ['PRECO', 'SETOR']

    setor = df[df['SETOR'] == df.loc[ticker]['SETOR']]
    res = dict()
    for col in df.columns:
        if col in skip:
            continue
        res[col] = {
            'bruto': df.loc[ticker][col],
            'geral': df[col].apply(np.log10),
            'setor': setor[col].apply(np.log10)
        }
    return res


def gen_rows(ticker: str, data: dict):
    rows = []
    row = []
    for col, val in data.items():
        modifier = view_modifiers.get(col, lambda x: x)
        bruto = modifier(data[col]["bruto"])
        row.append(
            dbc.Col(
                card(
                    [f'{col}: ',  f'{bruto}'],
                    [
                        html.H6('No setor'),
                        *progress_graph(ticker, data[col]['setor']),
                        html.Hr(),
                        html.H6('Geral'),
                        *progress_graph(ticker, data[col]['geral']),
                    ]
                )
            )
        )
        if len(row) == 2:
            rows.append(dbc.Row(row))
            rows.append(html.Hr())
            row = []

    return rows


def render_welcome():
    return [dbc.Spinner(html.Div(id="loading-recomm")),
            html.Hr(),
            dbc.Spinner(html.Div(id="loading-variat"))]


@ app.callback(Output("loading-recomm", "children"),
               [Input('url', 'pathname')])
def load_recommendations(pathname):
    return dbc.Row(dbc.Col(card(['Recomendações do mês', html.Hr(), html.Small('indicações de corretoras e analistas')],
                                dbc.Table.from_dataframe(get_top5(), striped=True, bordered=True, hover=True))))


@ app.callback(Output("loading-variat", "children"),
               [Input('url', 'pathname')])
def load_variations(pathname):
    variations = top_variations()
    return dbc.Row([
        dbc.Col(card('Maiores altas 24h',
                     dbc.Table.from_dataframe(variations['altas'], striped=True, bordered=True, hover=True), color='success', outline=True)),
        dbc.Col(card('Maiores baixas 24h',
                     dbc.Table.from_dataframe(variations['baixas'], striped=True, bordered=True, hover=True), color='danger', outline=True))
    ])


def get_graham(stock):
    if stock['VPA'] < 0 or stock['LPA'] < 0:
        return 0
    else:
        return (stock['VPA'] * stock['LPA'] * 22.5) ** .5


if __name__ == '__main__':
    app.run_server(debug=True)
