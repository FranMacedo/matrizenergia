
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import copy
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

ctx = dash.callback_context

color_7_live = ["#8DD3C7", "#fff069", "#BEBADA", "#FB8072", "#80B1D3", "#FDB462", "#B3DE69"]
color_7_dead = ["#d3ede9", "#FFF9C4", "#e3e1ed", "#f5d4d0", "#cee1ed", "#fae0c3", "#e7f2d3"]


color_5_live = ["#f48b84", "#72afae", "#ffe0ae", "#ff6f69", "#96ceb4"]
color_5_dead = ["#f5c0bc", "#b6e3e2", "#ffebc9", "#f5c1bf", "#d1e8dd"]

color_7_live_d = {"Diesel": color_7_live[0],
                    "Electricidade": color_7_live[1],
                    "Fuel": color_7_live[2],
                    "Gás Natural": color_7_live[3],
                    "Gasolina": color_7_live[4],
                    "GPL": color_7_live[5],
                    "Outros": color_7_live[6]}

color_7_dead_d = {"Diesel": color_7_dead[0],
                    "Electricidade":color_7_dead[1],
                    "Fuel": color_7_dead[2],
                    "Gás Natural": color_7_dead[3],
                    "Gasolina": color_7_dead[4],
                    "GPL": color_7_dead[5],
                    "Outros": color_7_dead[6]}

color_5_live_d = {"Agricultura": color_5_live[0],
                    "Doméstico": color_5_live[1],
                    "Indústria": color_5_live[2],
                    "Serviços": color_5_live[3],
                    "Transportes": color_5_live[4]}

color_5_dead_d = {"Agricultura": color_5_dead[0],
                    "Doméstico": color_5_dead[1],
                    "Indústria": color_5_dead[2],
                    "Serviços": color_5_dead[3],
                    "Transportes": color_5_dead[4]}

unidades_emissoes = 'ton'
unidades_energia = 'tep'


def cria_df(file_path):
    forma_df = pd.read_excel(file_path)

    # errados = ['Indústria', 'Serviços', 'Doméstico']
    # correctos = ['Industria', 'Servicos', 'Domestico']
    # forma_df = forma_df.replace(errados, correctos)
    forma_df.rename(columns={'Outros ': 'Outros'}, inplace=True)

    # aa = forma_df.loc[forma_df['Ano'] == 2016, :]
    # aa = aa.iloc[:, 1:-1]
    # aa_sum = aa.to_numpy().sum()

    forma_df.fillna(0, inplace=True)
    anos = list(forma_df.Ano.unique())
    # numero_anos = len(anos)
    forma_df_sem_ano = forma_df.iloc[:, :-1]
    forma_sector_df = forma_df_sem_ano.groupby(['Sector']).sum()
    forma_anual = forma_df.groupby(['Ano']).sum()
    forma_anual['Total'] = forma_anual.sum(axis=1)

    sector_df = forma_df.transpose().copy()
    sector_df.rename(columns=sector_df.iloc[0], inplace=True)
    sector_df.drop('Sector', inplace=True)
    sector_df_temp = sector_df.iloc[:7, 0:5].copy()
    sector_df_temp['Ano'] = anos[0]
    sector_df_temp.reset_index(inplace=True)
    sector_df_temp.rename(columns={'index': 'Forma'}, inplace=True)

    for ano in anos[1:]:
        df = sector_df.loc[:, sector_df.loc['Ano', ] == ano].copy()
        df.loc[:, 'Ano'] = ano
        df.drop('Ano', axis=0, inplace=True)
        df.reset_index(inplace=True)
        df = df.rename(columns={'index': 'Forma'})

        sector_df_temp = pd.concat([sector_df_temp, df], ignore_index=True)

    sector_df = sector_df_temp
    sector_anual = sector_df.groupby(['Ano']).sum()
    sector_anual.drop('Forma', axis=1, inplace=True)

    forma_list = sorted(forma_df.columns[1:-1].tolist())
    sector_list = sorted(sector_df.columns[1:-1].tolist())
    forma_df = forma_df.round(0)
    sector_df = sector_df.round(0)
    forma_anual = forma_anual.round(0)
    sector_anual = sector_anual.round(0)
    forma_sector_df = forma_sector_df.round(0)

    forma_df['color_fill'] = forma_df['Sector'].apply(lambda x: color_5_dead_d[x])
    forma_df['color_line'] = forma_df['Sector'].apply(lambda x: color_5_live_d[x])

    sector_df['color_fill'] = sector_df['Forma'].apply(lambda x: color_7_dead_d[x])
    sector_df['color_line'] = sector_df['Forma'].apply(lambda x: color_7_live_d[x])


    # forma_df['color_dead'] = color_5_dead * len(anos)
    # forma_df['color_live'] = color_5_live * len(anos)
    #
    # sector_df['color_dead'] = color_7_dead * len(anos)
    # sector_df['color_live'] = color_7_live * len(anos)

    return forma_df, sector_df, forma_anual, sector_anual, forma_sector_df, forma_list, sector_list, anos


def change_df(which_df, primaria_final):
    if primaria_final == 'primaria':
        forma_df, sector_df, forma_anual, sector_anual, forma_sector_df = forma_df_fi, sector_df_fi, forma_anual_fi, \
                                                                          sector_anual_fi, forma_sector_df_fi
    else:
        forma_df, sector_df, forma_anual, sector_anual, forma_sector_df = forma_df_pr, sector_df_pr, forma_anual_pr, \
                                                                          sector_anual_pr, forma_sector_df_pr

    return {
        "forma_df": forma_df,
        "sector_df": sector_df,
        "forma_anual": forma_anual,
        "sector_anual": sector_anual,
        "forma_sector_df": forma_sector_df,
    }[which_df]

    # return forma_df, sector_df, forma_anual, sector_anual, forma_sector_df


def cria_cores(cores_5_7, select):
    if cores_5_7 == 5:
        color_dead = color_5_dead
        color_live = color_5_live
        selec_list = sector_list

    else:
        color_dead = color_7_dead
        color_live = color_7_live
        selec_list = forma_list

    colors = color_dead.copy()
    selecao_posi = selec_list.index(select)
    cor_viva = color_live[selecao_posi]
    colors[selecao_posi] = cor_viva

    return colors


energia_final_path = "data/energia_final.xlsx"
energia_primaria_path = "data/energia_primaria.xlsx"
emissoes_path = "data/emissoes_CO2.xlsx"


forma_df_fi, sector_df_fi, forma_anual_fi, sector_anual_fi, forma_sector_df_fi, forma_list, sector_list, anos \
    = cria_df(energia_final_path)

forma_df_pr, sector_df_pr, forma_anual_pr, sector_anual_pr, forma_sector_df_pr, forma_list_pr, sector_list_pr, \
    anos_pr = cria_df(energia_primaria_path)

forma_df_em, sector_df_em, forma_anual_em, sector_anual_em, forma_sector_df_em, forma_list_em, sector_list_em, \
    anos_em = cria_df(emissoes_path)

# Total de energia em texto e milhões
total_m_fi = list(round(forma_anual_fi['Total'] / 1000000, 1))
total_m_fi = list(map(str, total_m_fi))
total_m_fi = [a + 'M' for a in total_m_fi]

total_m_pr = list(round(forma_anual_pr['Total'] / 1000000, 1))
total_m_pr = list(map(str, total_m_pr))
total_m_pr = [a + 'M' for a in total_m_pr]

total_m_em = list(round(forma_anual_em['Total'] / 1000 / 1000000, 1))
total_m_em = list(map(str, total_m_em))
total_m_em = [a + 'M' for a in total_m_em]

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

layout = dict(
    font=dict(
        size=13,
        family="'Abel', sans-serif",
    ),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",

)
#
# SIDEBAR_STYLE = {
#     # "position": "fixed",
#     "top": 0,
#     # "margin-top": 100,
#     "left": 0,
#     # "bottom": 0,
#     'height': '100%',
#     "width": "40rem",
#     "padding": "2rem 1rem",
#     "background-color": "#f8f9fa",
#     "float": "left",
#     "position": "absolute",
#     "z - index": 99999,
#     "box-shadow": "2px 2px 2px lightgrey"
# }

SIDEBAR_STYLE = {
    "background-color": "#f8f9fa",
    "padding": "10% 1%",
    'height': '100%',
    'font-family': layout['font']['family']
}



    # 'padding-bottom': '99999px', 'margin-bottom': '-99999px'
#
#
# INSIDE_STYLE = {
#     "margin-left": "2rem",
#     "margin-right": "2rem",
#     "padding": "2rem 2rem",
# }
#
CONTENT_STYLE_1 = {
    "padding": "2%",
    'height': '98%',
    'font-family': layout['font']['family']

}

CONTENT_STYLE_2 = {
    "padding": "2%",
    'height': '100%',
    'font-family': layout['font']['family']

}

# cartao com butoes final/primaria


card_final_primaria = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.P("Seleccione a forma de energia:",
                               ), width={"size": 6}),

                dbc.Col(
                    dcc.Dropdown(
                        id='dd-primaria-final',
                        options=[{'label': 'Primária', 'value': 'Primária'},
                                   {'label': 'Final', 'value': 'Final'}],
                        clearable=False,
                        value='Final',
                        style= dict(font=layout['font'])

                    ), width=6
                ),
            ],
            align="center", justify='center'
        ),
    ]
)


# cartao com butoes forma/sector
card_forma_sector = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.P(id='header-forma-sector',
                               ), width={"size": 6}),

                dbc.Col(
                    dcc.Dropdown(
                        id='dd-forma-sector',
                        options=[{'label': 'Forma', 'value': 'Forma'},
                                 {'label': 'Sector', 'value': 'Sector'}],
                        clearable=False,
                        value='Forma'
                    ), width=6
                ),
            ],
            align="center", justify='center'
        ),
    ]
)


# slider + grafico de barras
year_selector = html.Div([
    html.Br(),
# "<br>(Seleccione o ano pretendido)"
    html.P(id='header-ano-bar', style={'textAlign': 'center', "padding": "0% 0% 0% 0%"}),
    html.P("(Seleccione o ano pretendido)", style={'textAlign': 'center', "padding": "0% 0% 10% 0%", 'font-style': 'italic'}),

    dcc.Loading(id="loading-ano-bar", type="circle",
                children=[
                    dcc.Graph(id="ano-bar-graph", config={'displayModeBar': False})]),

    html.Div([dcc.Slider(id='year-selected', min=min(anos), max=max(anos), value=min(anos),
                         marks={str(ano): str(ano) for ano in anos})],
             style={'textAlign': "center", "margin-left": "1rem", "margin-right": "1rem", "padding": "1rem 1rem"}
             )
        ])


# Barra lateral, que engloba todas as componentes geradas em cima
sidebar = html.Div(
    [
        # html.H3("Matriz de Energia", className="display-6"),
        # html.Hr(),

        dbc.Tabs(
                [
                    dbc.Tab([
                             html.Br(),
                             html.Div([card_final_primaria], style={"padding": "0% 10% 0% 10%"}),
                             html.Hr(),

                             ], label="Energia", tab_id="tab-energia",
                            tab_style={'width': '50%', 'textAlign': 'center'}),

                    dbc.Tab([html.Br()],
                            label="Emissões", tab_id="tab-emissoes",
                            tab_style={'width': '50%', 'textAlign': 'center'}),
                ],
                id="tabs",
                # card=True,
                active_tab="tab-energia",
        ),

        html.Div([card_forma_sector], style={"padding": "0% 10% 0% 10%"}),
        html.Hr(),
        year_selector
    ],
    style=SIDEBAR_STYLE,
    className="pretty_container",
)


# Donut Container
donut_container = html.Div([

                    dbc.Row(
                        [
                            html.Div([html.P(id='header-donut',
                                             style={"textAlign": "center", 'margin': 'auto', 'padding': '8px'}
                                             )
                                      ],
                                     className="twelve columns")
                        ],
                        style={"textAlign": "center"}, className="pretty_container_2 row"
                    ),

                    dbc.Row(
                        [
                            html.Div([dcc.Loading(id="loading-donut", type="circle",
                                                  style={'margin-left': '0%', 'margin-top': '10%'},
                                                  children=[dcc.Graph(id="donut-graph", config={'displayModeBar': False})])],

                                    # align="center"
                                     className="ten columns",
                                     # style={
                                     #     "margin-left": "10%",
                                     # #     "margin-bottom": "0%",
                                     # #     "bottom": 0,
                                     #     "padding": "1% 1% 15% 0%",
                                     # },
                                     )
                        ],
                        justify='center'
                        # className="row"
                    )

                ],
                    style=CONTENT_STYLE_1,
                    className="pretty_container")


# single bar Container
single_bar_container = html.Div([
                    html.Div(
                        [
                            # html.Abbr("\u003f\u20dd", title="Hello, I am hover-enabled helpful information."),

                            html.Div(
                                [
                                    dbc.Col([

                                        html.P(id='text-bar',
                                               style={"textAlign": "center", 'margin': 'auto', 'padding': '8px'}),
                                        ]),

                                ],

                                id='text-bar-div',
                                className="bare_container twelve columns",
                                style={"textAlign": "center"}),
                        ],
                        className="pretty_container_2 row"
                    ),
                    html.Div(
                        [
                            dbc.Row([
                                dbc.Col(html.Div(id='select-dd-text'), width=5),
                                dbc.Col(
                                    dcc.Dropdown(
                                        id='dropdown-single',
                                        clearable=False,
                                            ), width=4
                                ),
                                dbc.Col(html.Div(id='value-dd-text'), width=3,
                                        style={'font-size': 13, 'font-weight': 'bold', "textAlign": "center"})
                            ],  no_gutters=True, justify='center', align="center"),

                            html.Hr(),



                            html.Div([dcc.Loading(id="loading-single-bar", type="circle",
                                                  style={'margin-left': '0%', 'margin-top': '10%'},
                                                  children=[html.Div([dcc.Graph(id="bar-single-graph", config={'displayModeBar': False})],
                                                                     id='single_bar_div')]
                                                  )
                                      ],
                                     )
                        ],
                    )

                ],

    # id='single_bar_container',

    style=CONTENT_STYLE_1,
    className="pretty_container",
)

year_line_container = html.Div([
    html.Div(
        [
            html.Div([html.P(id='header-ano-line',
                             style={"textAlign": "center", 'margin': 'auto', 'padding': '8px'}
                             )
                      ],
                     className="twelve columns")
        ],
        style={"textAlign": "center"}, className="pretty_container_2 row"
    ),

    html.Div(
        [
            dcc.Loading(
                id="loading-ano-line",
                type="circle",
                children=[dcc.Graph(id="ano-line-graph", config={'displayModeBar': False})]
            )
        ],
        className="twelve columns"
    )
],
    className="pretty_container",
    style=CONTENT_STYLE_2
)
# ], id='single_bar_container', style={'display': 'none'})

app.layout = html.Div([
    # dcc.Store(id='memory_p_f'),
    dcc.Store(id='memory_s_f'),

    dbc.Row(
        [
            dbc.Col(sidebar, width=4, style=dict(font=layout['font'])),

            dbc.Col([

                dbc.Row([
                    dbc.Col(donut_container, width=6),
                    dbc.Col(single_bar_container, width=6),
                ], justify="start"),

                dbc.Row([
                    dbc.Col(year_line_container, width=12)
                ], justify="start")

            ],
                width=8)

        ],
        justify="start"

    )
],
)


#
#
# @app.callback(
#     [Output("primaria", "active"),
#      Output("final", "active"),
#      # Output("memory-output", "data")
#      ],
#     [Input('primaria', 'n_clicks'),
#      Input('final', 'n_clicks'),
#      ],
#     [State('memory_p_f', 'data')]
# )
# def update_color_data_pf(primaria, final, memory_p_f):
#     if not ctx.triggered:
#         raise PreventUpdate
#
#     trigger = ctx.triggered[0]['prop_id'].split('.')[0]
#
#     memory_p_f = memory_p_f or {'final': 1, 'primaria': 0}
#
#     if trigger == 'primaria':
#         if memory_p_f['primaria'] == 1:
#             return dash.no_update, dash.no_update
#         else:
#             # datasets = {
#             #     'forma_df': forma_df_pr.to_json(orient='split'),
#             #     'sector_df': sector_df_pr.to_json(orient='split'),
#             #     'forma_anual': forma_anual_pr.to_json(orient='split'),
#             #     'sector_anual': sector_anual_pr.to_json(orient='split'),
#             #     'forma_sector_df': forma_sector_df_pr.to_json(orient='split')
#             # }
#             return True, False
#     else:
#         if memory_p_f['final'] == 1:
#             return dash.no_update, dash.no_update
#         # datasets = {
#         #     'forma_df': forma_df_fi.to_json(orient='split'),
#         #     'sector_df': sector_df_fi.to_json(orient='split'),
#         #     'forma_anual': forma_anual_fi.to_json(orient='split'),
#         #     'sector_anual': sector_anual_fi.to_json(orient='split'),
#         #     'forma_sector_df': forma_sector_df_fi.to_json(orient='split')
#         # }
#         else:
#             return False, True
#         # json.dumps(datasets)
#
#
# @app.callback(
#     [Output("sector", "active"),
#      Output("forma", "active")],
#     [Input('dd-forma-sector', 'value')]
# )
# def update_color_sf(form_sect):
#     if not ctx.triggered:
#         raise PreventUpdate
#
#     trigger = ctx.triggered[0]['prop_id'].split('.')[0]
#
#     if form_sect == 'Sector':
#         return True, False
#
#     else:
#         return False, True


@app.callback(
    Output("year-selected", "value"),
    [Input("ano-bar-graph", "clickData")])
def update_year_slider(ano_bar_graph_selected):
    if not dash.callback_context.triggered:
        raise PreventUpdate

    if ano_bar_graph_selected is None:
        return 2016
    else:
        return ano_bar_graph_selected['points'][0]['x']


# 'Consumo total de Energia por ano (tep)')


@app.callback([Output('header-ano-bar', 'children'),
               Output('header-forma-sector', 'children')],
              [Input('tabs', 'active_tab'),
               Input('dd-primaria-final', 'value')
               ]
              )
def headers_emissoes(at, prim_fin):
    if not dash.callback_context.triggered:
        raise PreventUpdate
    if at == "tab-emissoes":
        return 'Emissões de CO2 por ano (ton/tep)', 'Emissões de CO2 por:'

    else:
        head_a_b = 'Consumo total de Energia {} anual (tep)'.format(prim_fin)
        return head_a_b, 'Seleccione a desagragação pretendida:'


@app.callback(

    Output("ano-bar-graph", "figure"),

    [Input("year-selected", "value"),
     Input('dd-primaria-final', 'value'),
     Input('tabs', 'active_tab'),
     ]

)
def update_ano_bar(ano, prim_fin, at):


    if not ctx.triggered:
        raise PreventUpdate

    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    trigger_value = ctx.triggered[0]['value']




    if at == "tab-emissoes":

        forma_anual = forma_anual_em
        total_m = total_m_em
        unidade = unidades_emissoes

    else:
        unidade = unidades_energia

        if prim_fin == 'Primária':
            forma_anual = change_df('forma_anual', 'primaria')
            total_m = total_m_pr
        else:
            forma_anual = change_df('forma_anual', 'final')
            total_m = total_m_fi


    layout_ano_bar = copy.deepcopy(layout)

    ano_posi = list(forma_anual.index).index(ano)
    color_fill = ['#9BD7F1', ] * len(forma_anual.index)
    color_fill[ano_posi] = '#029CDE'
    color_line = ['#029CDE', ]*len(forma_anual.index)

    my_text = ['Total: ' + '{:.0f}'.format(tr) + ' | ' + unidade + '<br>Ano: ' + '{}'.format(an)
               for tr, an in zip(list(forma_anual['Total']), anos)]
    fig = go.Figure(data=[go.Bar(
        x=forma_anual.index,
        y=forma_anual['Total'],
        marker_color=color_fill,
        marker_line_color=color_line,
        text=total_m,
        hovertext=my_text,
        hoverinfo='text',
        textposition='outside',
        hoverlabel=dict(font=dict(family=layout['font']['family'])),


    )])

    layout_ano_bar['margin'] = dict(l=0, r=0, b=0, t=0)
    layout_ano_bar['height'] = 200
    layout_ano_bar['dragmode'] = 'select'
    fig.update_layout(layout_ano_bar)
    # fig.update_layout(height=350)
    fig.update_yaxes(automargin=True, range=[0, max(forma_anual['Total'])*1.15],
                     autorange=False, fixedrange=True, showticklabels=False)
    fig.update_xaxes(fixedrange=True)

    # fig.update_yaxes()
    return fig


@app.callback([Output('header-ano-line', 'children'),
              Output('header-donut', 'children')],
              [Input("year-selected", "value"),
               Input('tabs', 'active_tab'),
               Input('dd-primaria-final', 'value'),
               Input('dd-forma-sector', 'value')
               ],

              )
def header_donut_ano_line(ano, at, prim_fin, form_sect):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate

    if at == "tab-emissoes":
        unidade = unidades_emissoes

        text_1 = "Emissões de CO2"
        text_1_1 = ' anuais'
    else:
        unidade = unidades_energia

        text_1 = "Consumo de Energia"
        text_1_1 = ' anual'


        if prim_fin == 'Primária':
            text_1 = text_1 + " Primária"
        else:
            text_1 = text_1 + " Final"

    if form_sect == "Sector":
        text_2 = ', por Sector de Consumo'
    else:
        text_2 = ', por Forma de Energia'

    ano_format = ', em ' + str(ano)
    texto_donut = text_1 + text_2 + ano_format
    texto_line = text_1 + text_1_1 + text_2 + " ({})".format(unidade)

    return texto_line, texto_donut


# Donut Total
@app.callback(
    Output("donut-graph", "figure"),
    [Input("year-selected", "value"),
     Input('dd-forma-sector', 'value'),
     Input('donut-graph', 'clickData'),
     Input('tabs', 'active_tab'),
     Input('dropdown-single', 'value'),
     Input('dd-primaria-final', 'value'),
     ]
)
def update_donut(ano, form_sect, selecao, at, dd_select, prim_fin):

    if not ctx.triggered:
        raise PreventUpdate

    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    trigger_value = ctx.triggered[0]['value']


    layout_donut = copy.deepcopy(layout)


    if at == "tab-emissoes":
        forma_anual = forma_anual_em / 1000
        sector_anual = sector_anual_em / 1000
        unidade = unidades_emissoes
    else:
        unidade = unidades_energia

        if prim_fin == 'Primária':
            sector_anual = change_df('sector_anual', 'primaria')
            forma_anual = change_df('forma_anual', 'primaria')
        else:
            sector_anual = change_df('sector_anual', 'final')
            forma_anual = change_df('forma_anual', 'final')

    # seleciona Sector
    if form_sect == 'Sector':

        s_f_lista = sector_list
        color_live = color_5_live_d
        color_dead = color_5_dead_d
        df = sector_anual

        if dd_select:

            if dd_select in sector_list:
                select = dd_select

            else:
                select = 'Transportes'


        elif selecao:

            select_1 = selecao['points'][0]['label']
            if select_1 in sector_list:

                select = select_1

            else:
                select = 'Transportes'

        else:
            select = 'Transportes'

    # seleciona Forma
    else:
        s_f_lista = forma_list

        df = forma_anual.iloc[:, :-1]
        color_live = color_7_live_d
        color_dead = color_7_dead_d

        if dd_select:

            if dd_select in forma_list:
                select = dd_select
            else:
                select = 'Electricidade'

        elif selecao:

            select_1 = selecao['points'][0]['label']

            if select_1 in forma_list:
                select = select_1
            else:
                select = 'Electricidade'

        else:
            select = 'Electricidade'


    layout_donut['legend'] = go.layout.Legend(

                            x=1.1,
                            # y=-0.2,
                            traceorder="normal",
                            font=dict(
                                size=13,
                                color="black"
                            ),
                            bgcolor='rgba(0,0,0,0)',
                            orientation='v'
                            )
    layout_donut['autosize'] = True

    # filtra por ano, atribui cores e remove os valores nulos

    df = df.loc[ano, :].to_frame()

    df.sort_index(inplace=True)
    df['labels'] = df.index

    # s_f_lista_cut = s_f_lista.copy()
    # s_f_lista_cut.remove(select)

    df['color_fill'] = df['labels'].apply(lambda x: color_dead[x])
    df['color_line'] = df['labels'].apply(lambda x: color_live[x])

    # for c in s_f_lista_cut:
    #     df.loc[(df.index == c), 'color_fill'] = color_dead[c]
    #     df.loc[(df.index == c), 'color_line'] = color_live[c]

    df.loc[(df.index == select), 'color_fill'] = color_live[select]


    df = df[(df != 0).all(1)]
    df = df.drop(['labels'], axis=1)

    my_text_hover = [fs + ': ' + '{:.0f}'.format(sel) + ' | ' + unidade + '<br>Ano: ' + '{}'.format(ano)
                     for fs, sel in zip(df.index.tolist(), list(df[ano]))]

    my_text_write = [fs + ': ' + '{:.0f}'.format(sel) + ' | ' + unidade + '<br>Ano: ' + '{}'.format(ano)
                     for fs, sel in zip(df.index.tolist(), list(df[ano]))]

    fig = go.Figure(data=[go.Pie(labels=df.index.tolist(),
                    values=df[ano].tolist(),
                    hole=0.3,
                    marker=dict(colors=df['color_fill'], line=dict(color=df['color_line'], width=2)),
                    textinfo='percent',
                    hovertext=my_text_hover,
                    hoverinfo='text',
                    hoverlabel=dict(font=dict(size=13, family=layout['font']['family'])),
                    opacity=0.8,
                    sort=False)])


    layout_donut['margin'] = dict(l=0, r=0, b=20, t=10)
    # layout_donut['autosize'] = True

    # anot = [go.layout.Annotation(
    #         text=select + '<br>' + str(df.loc[df.index == select, ano].item()) + ' | ' + unidade,
    #     showarrow=False,
    #     )]

    fig.update_layout(layout_donut)
    # fig.update_layout(annotations=anot)



    return fig


@app.callback(
    [Output('dropdown-single', 'options'),
     Output('dropdown-single', 'value')],
    [Input('dd-forma-sector', 'value'),
     Input('donut-graph', 'clickData')],

)
def update_dropdown_items(form_sect, selecao):
    if not ctx.triggered:
        raise PreventUpdate

    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    trigger_value = ctx.triggered[0]['value']

    if form_sect == 'Sector':
        items = [
            {'label': 'Serviços', 'value': 'Serviços'},
            {'label': 'Transportes', 'value': 'Transportes'},
            {'label': 'Doméstico', 'value': 'Doméstico'},
            {'label': 'Indústria', 'value': 'Indústria'},
            {'label': 'Agricultura', 'value': 'Agricultura'}
        ]

        if selecao is None:
            value = 'Transportes'
        else:
            value = selecao['points'][0]['label']

    else:
        items = [
            {'label': 'Electricidade', 'value': 'Electricidade'},
            {'label': 'Diesel', 'value': 'Diesel'},
            {'label': 'Gás Natural', 'value': 'Gás Natural'},
            {'label': 'Gasolina', 'value': 'Gasolina'},
            {'label': 'GPL', 'value': 'GPL'},
            {'label': 'Outros', 'value': 'Outros'}
        ]
        if selecao is None:
            value = 'Electricidade'
        else:
            value = selecao['points'][0]['label']

    return items, value

@app.callback(
    [Output("value-dd-text", "children"),
     Output("select-dd-text", "children"),
     Output("text-bar", "children"),
     Output("text-bar-div", "style"),
     Output("bar-single-graph", "figure")],
    [Input("year-selected", "value"),
     Input('dd-forma-sector', 'value'),
     Input('donut-graph', 'clickData'),
     Input('dd-primaria-final', 'value'),
     Input('tabs', 'active_tab'),
     Input('dropdown-single', 'value'),

     ]
)
def update_bar_single(ano, form_sect, selecao, prim_fin, at, dd_select):
    if not dash.callback_context.triggered:
        raise PreventUpdate

    if at == "tab-emissoes":
        sector_df = sector_df_em
        forma_df = forma_df_em
        unidade = unidades_emissoes
    else:

        unidade = unidades_energia

        if prim_fin == 'Primária':
            sector_df = change_df('sector_df', 'primaria')
            forma_df = change_df('forma_df', 'primaria')

        else:
            sector_df = change_df('sector_df', 'final')
            forma_df = change_df('forma_df', 'final')

    layout_bar_single = copy.deepcopy(layout)

    if form_sect == 'Sector':

        select_dd_text = "Seleccione o Sector de Energia:"

        df = sector_df
        forma_sector = 'Forma'

        if dd_select:
            if dd_select in sector_list:
                select = dd_select
            else:
                select = 'Transportes'

        elif selecao:
            pre_select = selecao['points'][0]['label']
            if pre_select in sector_list:
                select = pre_select
            else:
                select = 'Transportes'
        else:

            select = 'Transportes'

        prep_select = {
            'Agricultura': 'na',
            'Serviços': 'nos',
            'Indústria': 'na',
            'Transportes': 'nos',
                       }
        if at == "tab-emissoes":
            if select == 'Doméstico':
                title_1 = 'Emissões de CO2 no sector ' + select
            else:
                title_1 = 'Emissões de CO2 ' + prep_select[select] + ' ' + select

        else:
            if select == 'Doméstico':
                title_1 = 'Consumo' + " " + select + " de Energia"
            else:
                title_1 = 'Consumo' + " de Energia " + prep_select[select] + " " + select

        select_posi = sector_list.index(select)
        bg_color = color_5_dead_d[select]
        title = title_1 + ", por Forma de Energia, em " + str(ano)

    else:

        select_dd_text = "Seleccione o Tipo de Energia:"
        df = forma_df

        # title = "Consumo de Energia por forma de consumo"
        forma_sector = 'Sector'

        if dd_select:
            if dd_select in forma_list:
                select = dd_select
            else:
                select = 'Electricidade'


        elif selecao:
            pre_select = selecao['points'][0]['label']
            if pre_select in forma_list:
                select = pre_select
            else:
                select = 'Electricidade'
        else:

            select = 'Electricidade'

        if at == "tab-emissoes":
            title_1 = "Emissões de CO2 geradas no Consumo de"
        else:
            title_1 = "Consumo de "
        title = title_1 + " " + select + ", por Sector de Consumo, em " + str(ano)



        bg_color = color_7_dead_d[select]

    df = df.loc[(df['Ano'] == ano), [forma_sector, select, 'color_fill', 'color_line']]


    df = df[(df != 0).all(1)]
    df = df.sort_values(forma_sector)
    df['Percentagem'] = df[select]/(df[select].sum())*100

    my_text_hover = [fs + '<br>' + '{:.0f}'.format(sel) + ' | ' + unidade + '<br>' + '{:.2f}'.format(pr)
                     + '%' + '<br>Ano: ' + '{}'.format(ano)
                     for fs, sel, pr in zip(list(df[forma_sector]), list(df[select]), list(df['Percentagem']))]

    my_text_show = ['{:.0f}'.format(pr) + '%' for pr in list(df['Percentagem'])]

    fig = go.Figure(data=[go.Bar(
        x=df[select],
        y=df[forma_sector],
        marker_color=df['color_fill'],
        orientation='h',
        opacity=0.8,
        marker_line_color=df['color_line'],
        marker_line_width=1.5,
        text=my_text_show,
        hovertext=my_text_hover,
        hoverinfo='text',
        hoverlabel=dict(font=dict(size=13, family=layout['font']['family'])),
        textposition='auto'

    )])
    style = {"textAlign": "center", "backgroundColor": bg_color}
    layout_bar_single['margin'] = dict(l=0, r=0, b=0, t=0)
    layout_bar_single['height'] = 300
    layout_bar_single['hovermode'] = "y"
    #layout_bar_single['title'] = dict(text=select, font=dict(size=13), xref='paper', x=0.3)

    fig.update_layout(layout_bar_single)
    valor_total = str(int(round(df[select].sum(),0)))

    value = "                         " + valor_total + " " + unidade

    return value, select_dd_text, title, style, fig


@app.callback(
    Output("ano-line-graph", "figure"),
    [Input("year-selected", "value"),
     Input('dd-forma-sector', 'value'),
     Input('dd-primaria-final', 'value'),
     Input('tabs', 'active_tab')
     ]
)
def update_ano_line(ano, form_sect, prim_fin, at):
    if not dash.callback_context.triggered:
        raise PreventUpdate

    if at == "tab-emissoes":
        sector_anual = sector_anual_em
        forma_anual = forma_anual_em
        unidade = unidades_emissoes
        title_1 = "Emissões de CO2 anuais, por "
    else:
        unidade = unidades_energia
        title_1 = "Consumo de Energia {} anual, por ".format(prim_fin)


        if prim_fin == 'Primária':
            sector_anual = change_df('sector_anual', 'primaria')
            forma_anual = change_df('forma_anual', 'primaria')
            title_2 = prim_fin + " anual, por "

        else:
            sector_anual = change_df('sector_anual', 'final')
            forma_anual = change_df('forma_anual', 'final')

    layout_ano_line = copy.deepcopy(layout)

    if form_sect == 'Sector':
        df = sector_anual
        lista_index = list(df.sum().sort_values().index)
        color_line = [color_5_live_d[x] for x in lista_index]
        color_fill = [color_5_dead_d[x] for x in lista_index]
        # my_text = ['Agricultura: ' + '{:.0f}'.format(agr) + '<br>Indústria: ' + '{:.0f}'.format(ind) +
        #            '<br>Transportes: ' + '{:.0f}'.format(tran) + '<br>Serviços: ' + '{:.0f}'.format(serv)
        #            + '<br>Doméstico: ' + '{:.0f}'.format(dom) + '<br>' + '_' * 18 + '<br>' + '<br>TOTAL: ' + '{:.0f}'.format(
        #     agr + ind + tran + serv + dom)
        #            for agr, ind, tran, serv, dom in zip(list(df['Agricultura']), list(df['Indústria']),
        #                                                    list(df['Transportes']), list(df['Serviços']),
        #                                                    list(df['Doméstico']))]
        title_2 = '{0} de Consumo ({1})'.format(form_sect, unidade)

    else:
        df = forma_anual.iloc[:, :-1]
        lista_index = list(df.sum().sort_values().index)
        color_line = [color_7_live_d[x] for x in lista_index]
        color_fill = [color_7_dead_d[x] for x in lista_index]
        # my_text = ['Diesel: ' + '{:.0f}'.format(ds) + '<br>Electricidade: ' + '{:.0f}'.format(el) +
        #            '<br>Gás Natural: ' + '{:.0f}'.format(gn) + '<br>Gasolina: ' + '{:.0f}'.format(gl)
        #            + '<br>GPL: ' + '{:.0f}'.format(gpl) + '<br>Fuel: ' + '{:.0f}'.format(fu) + '<br>Outros: '
        #            + '{:.0f}'.format(out) + '<br>' + '_' * 18 + '<br>' + '<br>TOTAL: ' + '{:.0f}'.format(
        #     ds + el + gn + gl + gpl + fu + out)
        #            for ds, el, gn, gl, gpl, fu, out in zip(list(df['Electricidade']), list(df['Diesel']),
        #                                                    list(df['Gás Natural']), list(df['Gasolina']),
        #                                                    list(df['GPL']),
        #                                                    list(df['Fuel']), list(df['Outros']))]
        title_2 = '{0} de Energia ({1})'.format(form_sect, unidade)


    fig = go.Figure()
    i = 0
    title = title_1 + title_2

    for trace in df.sum().sort_values().index:
        my_text = [trace + ': ' + '{:.0f}'.format(tr) + ' | ' + unidade for tr in list(df[trace])]
        fig.add_trace(go.Scatter(x=anos, y=df[trace], stackgroup='one', name=trace, fillcolor=color_fill[i],
                                 line_color=color_line[i], hovertext=my_text, hoverinfo="text",
                                 hoverlabel=dict(bgcolor=color_fill[i],  font=dict(size=13))))
        i += 1

    layout_ano_line['legend'] = go.layout.Legend(
                            font=dict(
                                size=13,
                                color="black"
                            ))
    layout_ano_line['hovermode'] = "x"
    layout_ano_line['margin'] = dict(l=20, r=20, b=20, t=20)
    layout_ano_line['height'] = 300
    layout_ano_line['hoverlabel'] = dict(font=dict(family=layout['font']['family']))

    # layout_ano_line['title'] = dict(text=title, xref='paper', x=0.5)

    fig.update_layout(layout_ano_line)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
