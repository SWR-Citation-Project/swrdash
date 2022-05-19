import os
import pandas as pd
import plotly           #(version 4.5.0)
import plotly.express as px
import dash             #(version 1.8.0)
from dash import Dash, dcc, html, Input, Output, callback
from .lib.network_data.network_functions import create_row
import base64

dash.register_page(__name__, path="/by-race")

this_dir_img, _ = os.path.split(__file__)
image_filename = os.path.join(this_dir_img, "lib/assets", "cccc_logo.jpeg")
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

#---------------------------------------------------------------
# Import Data

df = pd.read_csv("./data/swr_pub_year_cited_grouped_indicator.csv")

#---------------------------------------------------------------
# Layout for Page

layout = html.Div([

    create_row(
        html.Header(
        [
            html.Div(
            html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), width="80px")
            ),
            html.Div(
            [
            html.H2("2012 - 2019 Publisher-to-Race Bar Chart"),
            html.P(
                "(For demonstration purposes only. Currently using generated race data with original data.)",
                className="disclaimer"
            ),
            html.P(
                "Explore the total number of cited authors' race across the discipline's journals. Use the slider at the bottom to adjust what years are displayed."
            )
            ]),
        ], 
        className="heatmap_header",
        id="header_banner")
    ),

    html.Div([
        dcc.Graph(id='our_graph')
    ]),

    # RANGESLIDER
    html.Div([
        html.Label(
          ['Choose Years:'],
          style={'font-weight': 'bold'}),
        html.P(),
        dcc.RangeSlider(
            id='my-range-slider', # any name you'd like to give it
            marks={
                2011: '2011',     # key=position, value=what you see
                2012: '2012',
                2013: '2013',
                2014: '2014',
                2015: '2015',
                2016: '2016',
                2017: '2017',
                2018: '2018',
                2019: '2019',
                # 2016: {'label': '2016', 'style': {'color':'#f50', 'font-weight':'bold'}},
            },
            step=1,                # number of steps between values
            min=2011,
            max=2019,
            value=[2011,2019],     # default value initially chosen
            dots=True,             # True, False - insert dots, only when step>1
            allowCross=False,      # True,False - Manage handle crossover
            disabled=False,        # True,False - disable handle
            pushable=2,            # any number, or True with multiple handles
            updatemode='mouseup',  # 'mouseup', 'drag' - update value method
            included=True,         # True, False - highlight handle
            vertical=False,        # True, False - vertical, horizontal slider
            verticalHeight=900,    # hight of slider (pixels) when vertical=True
            className='None',
            tooltip={
              'always_visible': True,  # show current slider values
              'placement':'bottom'
              },
            ),
    ]),

])

#---------------------------------------------------------------
# Connect range slider to bar plot

@callback(
    Output('our_graph','figure'),
    [Input('my-range-slider','value')]
)

def build_graph(years_chosen):

  # Filter data by list of years chosen: [year1,year2]
  dff = df[(df['citing_year']>=years_chosen[0]) & (df['citing_year']<=years_chosen[1])]

  fig = px.bar(
    dff, 
    x="race", 
    y="cited_total", 
    color='citing_publisher'
  )

  fig.update_layout(
    yaxis={
      'title':'Total number of cited scholars in journals by race'
    },
    title={
      'text':'Total number of cited scholars in journals by race',
      'font': {'size':28},'x':0.5,'xanchor':'center'}
  )

  return fig
    