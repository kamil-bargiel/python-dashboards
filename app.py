# -*- coding: utf-8 -*-
import dash
import dash_html_components as html
import plotly.express as px
import flask
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from scipy.interpolate import interp1d
import dash_core_components as dcc
from dash.dependencies import Input, Output

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
        dbc.NavItem(html.A("Summary", href="#summary", style = {'color': '#fff'}), className="mr-5"),
        dbc.NavItem(html.A("Daily Data", href="#nav-daily-graph", style = {'color': '#fff'}), className="mr-5"),
        dbc.NavItem(html.A("Global map", href="#map-view", style = {'color': '#fff'}), className="mr-5"),
    ],
    brand="kbargiel COVID-19 dashboard",
    brand_href="/",
    color="dark",
    dark=True,
    className="p-3 fixed-top"
)

world_tally = dbc.Container(
    [
        html.H2('World Data - summary', id='summary', style={'text-align': 'center', 'padding-top': '100px'}),

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
global_map_heading = html.H2(id='map-view', children='World map view', className='mt-5 py-4 pb-3 text-center')
map_fig = px.scatter_mapbox(country_df, lat="Lat", lon="Long", hover_name="Country", hover_data=["Confirmed", "Deaths"],
                        color_discrete_sequence=["#e60039"], zoom=2, height=500, size_max=50, size=circle_radius)
map_fig.update_layout(mapbox_style="open-street-map", margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=520)

daily_graph_heading = html.H2(id='nav-daily-graph', children='COVID-19 daily data and total cases ', className='mt-5 pb-3 text-center')

daily_country = confirmed_df['Country'].unique().tolist()
daily_country_list = []

my_df_type = ['Confirmed cases', 'Death rate', 'Recovered cases']
my_df_type_list = []

for i in daily_country:
    daily_country_list.append({'label': i, 'value': i})

for i in my_df_type:
    my_df_type_list.append({'label': i, 'value': i})

country_dropdown = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(children=[html.Label('Select Country'),
                                  html.Div(
                                      dcc.Dropdown(id='select-country', options=daily_country_list, value='India'))],
                        width=3, className='p-2 mr-5'),

                dbc.Col(children=[html.Label('Drage to choose no of Days', style={'padding-top': '0px'}),
                                  html.Div(dcc.Slider(id='select-date',
                                                      min=10,
                                                      max=len(death_df.columns[3:]),
                                                      step=1,
                                                      value=40
                                                      , className='p-0'), className='mt-3')],
                        width=3, className='p-2 mx-5'),

                dbc.Col(children=[html.Label('Select category', style={'padding-top': '0px'}),
                                  html.Div(dcc.Dropdown(id='select-category', options=my_df_type_list,
                                                        value='Confirmed cases'))],
                        width=3, className='p-2 ml-5'),
            ]
            , className='my-4 justify-content-center'),

    ]
)

app.layout = html.Div(
    [navbar, world_tally,
     html.Div(children = [global_map_heading,
         dcc.Graph(
             id='global_graph',
             figure=map_fig
         )
        ]
      ),
     dbc.Container([daily_graph_heading,
                    country_dropdown,
                    html.Div(id='country-total'),
                    dcc.Graph(
                        id='daily-graphs'
                    )
                    ]
                   ),
     ]
)

if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)


def daily_graph_gen(new_df, category):
    daily_data = []
    daily_data.append(go.Scatter(
        x=new_df['Date'], y=new_df['coronavirus'], name="Covid-19 daily report", line=dict(color='#f36')))

    layout = {
        'title': 'Daily ' + category + '  in ' + new_df['Country'].values[0],
        'title_font_size': 26,
        'height': 450,
        'xaxis': dict(
            title='Date',
            titlefont=dict(
                family='Courier New, monospace',
                size=24,
                color='#7f7f7f'
            )),
        'yaxis': dict(
            title='Covid-19 cases',
            titlefont=dict(
                family='Courier New, monospace',
                size=20,
                color='#7f7f7f'
            )),
    }

    figure = [{
        'data': daily_data,
        'layout': layout
    }]

    return figure


@app.callback(
    [Output('daily-graphs', 'figure')],
    [Input('select-country', 'value'),
     Input('select-category', 'value'),
     Input('select-date', 'value')]
)

def country_wise(country_name, df_type, number):
    # on select of category copy the dataframe to group by country
    if df_type == 'Confirmed cases':
        df_type = confirmed_df.copy(deep=True)
        category = 'COVID-19 confirmed cases'

    elif df_type == 'Death rate':
        df_type = death_df.copy(deep=True)
        category = 'COVID-19 Death rate'

    else:
        df_type = recovered_df.copy(deep=True)
        category = 'COVID-19 recovered cases'

    # group by country name
    country = df_type.groupby('Country')

    # select the given country
    country = country.get_group(country_name)

    # store daily death rate along with the date
    daily_cases = []
    case_date = []

    # iterate over each row
    for i, cols in enumerate(country):
        if i > 3:
            # take the sum of each column if there are multiple columns
            daily_cases.append(country[cols].sum())
            case_date.append(cols)
            zip_all_list = zip(case_date, daily_cases)

            # creata a data frame
            new_df = pd.DataFrame(data=zip_all_list, columns=['Date', 'coronavirus'])

    # append the country to the data frame
    new_df['Country'] = country['Country'].values[0]

    # get the daily death rate
    new_df2 = new_df.copy(deep=True)
    for i in range(len(new_df) - 1):
        new_df.iloc[i + 1, 1] = new_df.iloc[1 + i, 1] - new_df2.iloc[i, 1]
        if new_df.iloc[i + 1, 1] < 0:
            new_df.iloc[i + 1, 1] = 0

    new_df = new_df.iloc[-number:]

    return (daily_graph_gen(new_df, category))

