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

indicators = {
    'DY': 'Proventos pagos por uma companhia pelo preço atual de suas ações. Dividendos pagos / Preço atual da ação',
    'P/L': 'Dá uma ideia do quanto o mercado está disposto a pagar pelos lucros da empresa. Preço atual / Lucro por ação (LPA)',
    'P/VP': 'Preço atual / Valor patrimonial por ação (VPA)',
    'P/ATIVOS': 'Preço da ação / Ativos totais por ação.',
    'MARGEM BRUTA': 'Mede, objetivamente, o quanto a empresa ganha com a venda de seus produtos. Lucro bruto / Receita líquida',
    'MARGEM EBIT': 'Útil para comparar a lucratividade operacional de empresas do mesmo segmento, além de contribuir para avaliar o crescimento da eficiência produtiva de um negócio ao longo do tempo. EBIT / Receita Líquida',
    'MARG LIQUIDA': 'Revela a porcentagem de lucro em relação às receitas de uma empresa. Lucro Líquido / Receita Líquida',
    'P/EBIT': 'Preço da ação em relação ao seu resultado EBIT. O EBIT pode ser considerado uma aproximação do lucro operacional da empresa. Preço da ação / EBIT',
    'EV/EBIT': 'O EV (Enterprise Value ou Valor da Firma), indica quanto custaria para comprar todos os ativos da companhia, descontando o caixa. Este indicador mostra quanto tempo levaria para o valor calculado no EBIT pagar o investimento feito para compra-la.',
    'DIVIDA LIQUIDA/EBIT': 'Indica quanto tempo seria necessário para pagar a dívida líquida da empresa considerando o EBIT atual. Indica também o grau de endividamento da companhia.',
    'DIV LIQ/PATRI': 'Indica quanto de dívida uma empresa está usando para financiar os seus ativos em relação ao patrimônio dos acionistas. Dívida Líquida / Patrimônio Líquido',
    'PSR': 'Valor de mercado da empresa dividido pela receita operacional líquida ou preço da ação dividido pela receita líquida por ação. Preço atual / Receita líquida por ação',
    'P/CAP GIRO': 'Preço da ação dividido pelo capital de giro por ação. Capital de Giro é o Ativo Circulante menos Passivo Circulante.',
    'P AT CIR LIQ': 'Preço atual / Ativos Circulantes Líquidos por ação',
    'LIQ CORRENTE': 'Indica a capacidade de pagamento da empresa no curto prazo. Ativo Circulante / Passivo Circulante',
    'ROE': 'Mede a capacidade de agregar valor de uma empresa a partir de seus próprios recursos e do dinheiro de investidores. Lucro Líquido / Patrimônio Líquido',
    'ROA': 'O retorno sobre os ativos ou Return on Assets, é um indicador de rentabilidade, que calcula a capacidade de uma empresa gerar lucro a partir dos seus ativos, além de indiretamente, indicar a eficiência dos seus gestores. Lucro Líquido / Ativo total',
    'ROIC': 'Mede a rentabilidade que uma empresa é capaz de gerar em razão de todo o capital investido, incluindo os aportes por meio de dívidas. (EBIT - Impostos) / (Patrimônio Líquido + Endividamento)',
    'PATRIMONIO/ATIVOS': 'Patrimônio Líquido / Ativos totais',
    'PASSIVOS/ATIVOS': 'Passivos totais / Ativos totais',
    'GIRO ATIVOS': 'Mede se como uma empresa está utilizando o seu ativo (bens, investimentos, estoque etc.) para produzir riqueza, através da venda de seus produtos e/ou serviços. Receita líquida / Total médio de ativos',
    'CAGR RECEITAS 5 ANOS': 'CAGR (Compound Annual Growth Rate), ou taxa de crescimento anual composta, é a taxa de retorno necessária para um investimento crescer de seu saldo inicial para o seu saldo final',
    'LIQUIDEZ MEDIA DIARIA': 'Quantidade média em R$ de ações negociadas nos últimos 30 dias',
    'VPA': 'Indica qual o valor patrimonial de uma ação. Patrimônio Líquido / Número de ações',
    'LPA': 'Lucro por ação. Lucro Líquido / Número de ações',
    'PEG Ratio': 'O PEG Ratio é uma métrica de avaliação para determinar o trade-off relativo entre o preço de uma ação, o lucro gerado por ação e o crescimento esperado da empresa. Para o cálculo, assumimos o LPA Atual baseado nos últimos 4 trimestres, e o LPA Anterior os 4 trimestres anteriores a estes.(P/L) / [(LPA Atual / LPA Anterior) - 1]',
    'VALOR DE MERCADO': 'Número de ações * Preço atual da ação'
}