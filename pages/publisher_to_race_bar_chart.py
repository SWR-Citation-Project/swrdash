import os
import pandas as pd
import plotly           #(version 4.5.0)
import plotly.express as px
import dash             #(version 1.8.0)
from dash import dcc, html, Input, Output, callback
from .lib.network_data.network_functions import create_row
import base64

dash.register_page(__name__)
dash.register_page(
  __name__,
  name="Publisher-to-Race",
  order=2,
  title="Publisher-to-Race"
)

this_dir = os.path.abspath('./data')
this_dir_img, _ = os.path.split(__file__)
image_filename = os.path.join(this_dir_img, "lib/assets", "cccc_logo.jpeg")
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

#------------
# Import Data
df = pd.read_csv("./data/swr_pub_year_cited_grouped_indicator.csv")
__file__ = this_dir + '/pub_race_matrix.csv'
df_matrix = pd.read_csv(__file__, index_col='Citing Publisher')

# Goal: Use Intra-Percentages to create new values per pub
def find_intra_percentages(df):
  columns = df.columns.tolist()

  new_list_dict = []

  index = 0
  for row in df.to_dict('records'):

      publisher = list(df.index)[index]

      # Sum for row
      r_total = 0
      for r in row:

          r_total = r_total + row[r]

      row_values = {'Citing Publisher': publisher}
      for col in columns:
          
          rc = round(100 * (row[col]/r_total), 2)
          row_values.update({col: rc})

      new_list_dict.append(row_values)
      index = index + 1

  intra_df = pd.DataFrame(new_list_dict).set_index('Citing Publisher')

  return intra_df

intra_percentages_df = find_intra_percentages(df_matrix)

#----------------
# Layout for Page

layout = html.Div([

  # HEADER
  create_row(
      html.Header(
      [
          html.Div(
          html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),className="banner_logo_not_home")
          ),
          html.Div(
          [
          html.H2("2012 - 2019 Publisher-Race Analysis"),
          html.P(
              "(For demonstration purposes only. Currently using generated race data with original data.)",
              className="disclaimer"
          ),
          html.P(
              "Explore the total number of cited authors' race across the discipline's journals. Use the filters to adjust what data are displayed."
          )
          ]),
      ], 
      className="heatmap_header",
      id="header_banner")
  ),

  # BAR SELECTION AREA #
  html.Div([
    html.H2("Pub Race Bar Chart", style={"textAlign":"center"}),
    html.Hr(),
    html.P("Choose citation module of interest among the Top 20:"),
    # RANGESLIDER
    html.Div([
      html.Label(
        ['Choose Years:'],
        style={'font-weight': 'bold'}),
      html.P(),
      dcc.RangeSlider(
        id='my-range-slider',
        marks={
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
        min=2012,
        max=2019,
        value=[2012,2019],     # default value initially chosen
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
    html.Div(id="pub-race-bar-output", children=[]),
  ]),
  
  # HEATMAP FILTER
  html.Div([
    html.H2("Pub Race Heatmap", style={"textAlign":"center"}),
    html.Hr(),
    html.P("Filter by racial demographics:", className="filter_prompt"),
    dcc.Checklist(
        id="heatmap-race",
        options=[{"label": x, "value": x} for x in intra_percentages_df.columns],
        value=df_matrix.columns.tolist(),
    ),
    html.Div(id="pub-race-heatmap-output", children=[]),
  ]),

])

#---------------------------------------------------------------
# Connect range slider to bar plot

@callback(
  Output(component_id="pub-race-bar-output", component_property="children"),
  [Input(component_id="my-range-slider", component_property="value")]
)
def build_bar_chart(years_chosen):

  '''
    BAR CHART
  '''
  # Filter data by list of years chosen: [year1,year2]
  dff = df[(df['citing_year']>=years_chosen[0]) & (df['citing_year']<=years_chosen[1])]
  fig_bar_pub_race = px.bar(
    dff, 
    x="race", 
    y="cited_total", 
    color='citing_publisher'
  )
  fig_bar_pub_race.update_layout(
    yaxis={
      'title':'Total number of cited scholars in journals by race'
    },
    title={
      'text':'Total number of cited scholars in journals by race',
      'font': {'size':28},'x':0.5,'xanchor':'center'}
  )
  
  return [
    # BAR CHART
    html.Div([
      html.H3("Bar", style={"textAlign":"center", "margin-left": "25px","font-size":"1.25rem"}),
      html.Div(
        [dcc.Graph(figure=fig_bar_pub_race, id='pub-to-race-bar')],
        className="six columns"
      ),
    ], className="", style={"width": "100%"}),
  ]

'''
  HEATMAP
'''

# Labels for each heatmap cell
cell_copy = []
for cell_values in intra_percentages_df.values.tolist():
  cell_strings = []
  for cv in cell_values:
    cell_strings.append(str(cv))
  cell_copy.append(cell_values)

@callback(
  Output(component_id="pub-race-heatmap-output", component_property="children"),
  Input(component_id="heatmap-race", component_property="value")
)
def build_heatmap(cols):

  heatmap_figure = px.imshow(
    intra_percentages_df[cols],
    labels = dict(
        x="Racial Demographic", 
        y="Citing Publisher", 
        color="Total Citing by Race (%)"
    ),
    aspect="auto"
  )

  heatmap_figure.update_xaxes(side="top")
  
  return [
    # BAR CHART
    html.Div([
      html.H3("Bar", style={"textAlign":"center", "margin-left": "25px","font-size":"1.25rem"}),
      html.Div(
        [dcc.Graph(figure=heatmap_figure,id='pub-to-race-heatmap')],
        className="six columns"
      ),
    ], className="", style={"width": "100%"}),
  ]
    