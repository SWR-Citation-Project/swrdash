import os
import base64
import pandas as pd
import plotly           #(version 4.5.0)
import plotly.express as px
import dash             #(version 1.8.0)
from dash import html, dash_table
from .lib.network_data.network_functions import create_row

dash.register_page(__name__,
  path="/",
  order=0
)

# resolve path
this_dir, _ = os.path.split(__file__)
image_filename = os.path.join(this_dir, "lib/assets", "cccc_logo.jpeg")
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

df = pd.DataFrame()

#---------------------------------------------------------------
# Layout for Page

layout = html.Div([
  html.Div(
    dash_table.DataTable(
      columns=[
          {"name": i, "id": i, "deletable": False, "selectable": False} for i in df.columns
      ],
    ),
    style={'display': 'none'}
  ),
  create_row(
    html.Header([
        html.Div(
          html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()))
        ),
        html.Div([
          html.H2("[DEMO] SWR Citational Politics Dashboard"),
          html.P(
            "Currently this prototype is for demonstration purposes only. The original data has been combined with generated racical demographics to provide possible interactions.",
            className="disclaimer"
          ),
          html.P(
            "The original data has been combined with generated racical demographics to provide possible interactions."
          ),
        ], className="banner_copy_container"
      )], 
      className="index_banner",
      id="header_banner")
  ),
])