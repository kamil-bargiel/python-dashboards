# -*- coding: utf-8 -*-
import dash
import dash_html_components as html
import plotly.express as px
import flask
import pandas as pd
import dash_bootstrap_components as dbc
from scipy.interpolate import interp1d
import dash_core_components as dcc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)

death_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
confirmed_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
recovered_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
country_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv')

death_df.rename(columns={'Country/Region': 'Country'}, inplace=True)
confirmed_df.rename(columns={'Country/Region': 'Country'}, inplace=True)
recovered_df.rename(columns={'Country/Region': 'Country'}, inplace=True)
country_df.rename(columns={'Country_Region': 'Country', 'Long_': 'Long'}, inplace=True)

death_df.drop('Province/State', axis=1, inplace=True)
confirmed_df.drop('Province/State', axis=1, inplace=True)
recovered_df.drop('Province/State', axis=1, inplace=True)

country_df.sort_values(by='Confirmed', ascending=False, inplace=True)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(html.A("Daily Data", href="#nav-daily-graph", style = {'color': '#fff'}), className="mr-5"),
        dbc.NavItem(html.A("Most effected", href="#nav-top-country-graph", style = {'color': '#fff'}), className="mr-5"),
        dbc.NavItem(html.A("Comparison", href="#nav-cr-link", style = {'color': '#fff'}), className="mr-5"),
    ],
    brand="kbargiel COVID-19 dashboard",
    brand_href="/",
    color="dark",
    dark=True,
    className="p-3 fixed-top"
)

world_tally = dbc.Container(
    [
        html.H2('World Data - summary', style={'text-align': 'center', 'padding-top': '100px'}),

        dbc.Row(
            [
                dbc.Col(children=[html.H4('Confirmed cases'),
                                  html.Div(country_df['Confirmed'].sum(), className='text-info',
                                           style={'font-size': '34px', 'font-weight': '700'})],
                        width=3, className='text-center bg-light border-right p-2',
                        style={'border-top-left-radius': '6px', 'border-bottom-left-radius': '6px'}),
                dbc.Col(children=[html.H4('Recovered', style={'padding-top': '0px'}),
                                  html.Div(country_df['Recovered'].sum(), className='text-success',
                                           style={'font-size': '34px', 'font-weight': '700'})],
                        width=3, className='text-center bg-light border-right p-2'),
                dbc.Col(children=[html.H4('Deaths', style={'padding-top': '0px'}),
                                  html.Div(country_df['Deaths'].sum(), className='text-danger',
                                           style={'font-size': '34px', 'font-weight': '700'})],
                        width=3, className='text-center bg-light border-right p-2'),
                dbc.Col(children=[html.H4('Active cases'),
                                  html.Div(country_df['Active'].sum(), className='text-warning',
                                           style={'font-size': '34px', 'font-weight': '700'})],
                        width=3, className='text-center bg-light p-2',
                        style={'border-top-right-radius': '6px', 'border-bottom-right-radius': '6px'}),
            ]
            , className='my-4 shadow justify-content-center'),

    ]
)

margin = country_df['Confirmed'].values.tolist()
circle_range = interp1d([1, max(margin)], [0.2, 12])
circle_radius = circle_range(margin)
global_map_heading = html.H2(children='World map view', className='mt-5 py-4 pb-3 text-center')
map_fig = px.scatter_mapbox(country_df, lat="Lat", lon="Long", hover_name="Country", hover_data=["Confirmed", "Deaths"],
                        color_discrete_sequence=["#e60039"], zoom=2, height=500, size_max=50, size=circle_radius)
map_fig.update_layout(mapbox_style="open-street-map", margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=520)

app.layout = html.Div(
    [navbar, world_tally,
     html.Div(children = [global_map_heading,
         dcc.Graph(
             id='global_graph',
             figure=map_fig
         )
        ]
      )]
)

if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
