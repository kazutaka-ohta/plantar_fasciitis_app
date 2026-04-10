# import all modules
import dash
from dash import dcc, html
from flask import Flask
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Initiate the app
app = Flask(__name__)
app_dash = dash.Dash(__name__, server = app, url_base_pathname='/dashboard/', external_stylesheets=[dbc.themes.UNITED, dbc.icons.BOOTSTRAP])

# Route
app_dash.config.suppress_callback_exceptions = True
app_dash.config.update({
    'routes_pathname_prefix': 'dash_page',
    'requests_pathname_prefix': 'dash_page'
})

# Read the files
df =pd.read_excel('./data/predict_data.xlsx')

# Build the Components
# Header Components
Header_component = html.H1("Plantar Fasciitis Analysis Dashboard", style = {'color': 'darkcyan', 'text-align': 'center', 'font-size': '72px'})

# Visual Components
# Component1

scatterfig = px.scatter(df, x='age', y='pre_vas', color='weight', size='height')
scatterfig.update_layout(title = '年齢、体重と治療前の痛みの関係性')
scatterfig = go.FigureWidget(scatterfig)
# Component2

boxfig = px.box(df,x='gender',y='pre_vas',color='steroid',notched=False,points='all',title='ステロイド使用の有無における性別ごとの違い')
boxfig.update_layout(title = '箱ひげ図')
boxfig = go.FigureWidget(boxfig)

# Component3
piefig = px.pie(df,names=('gender'))
piefig.update_layout(title = '性別ごとの割合')
piefig = go.FigureWidget(piefig)

# Component4
sunburstfig = px.sunburst(df,path=['gender','sports_history'],)
sunburstfig.update_layout(title = '性別ごとのスポーツ歴')
sunburstfig = go.FigureWidget(sunburstfig)

# Component5
scatter3dfig = px.scatter_3d(df,x='d_flex',y='p_flex',z='pre_vas',size='weight',color='steroid',hover_data=['post_vas'])
scatter3dfig.update_layout(title = '3D散布図')
scatter3dfig = go.FigureWidget(scatter3dfig)

# Design the app layout
app_dash.layout = html.Div([
        dbc.Row(Header_component),
        dbc.Row([
            dbc.Col([dcc.Graph(figure = scatterfig)]),
            dbc.Col([dcc.Graph(figure = boxfig)]
        )]),
        dbc.Row([
            dbc.Col([dcc.Graph(figure = piefig)]),
            dbc.Col([dcc.Graph(figure = sunburstfig)]),
            dbc.Col(dcc.Graph(figure = scatter3dfig))
        ]),
])

# Run the App
app_dash.run_server(debug=True)