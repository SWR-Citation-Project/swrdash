import os
import dash
from dash import Dash, dcc, html, Input, Output, State, callback
from .lib.network_data.network_functions import create_row
import base64
import plotly.express as px
import pandas as pd

dash.register_page(
  __name__,
  name="Summary Statistics",
  order=1,
  title="Summary Statistics"
)

this_dir_img, _ = os.path.split(__file__)
image_filename = os.path.join(this_dir_img, "lib/assets", "cccc_logo.jpeg")
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

#------------
# Import Data
df = pd.read_csv("./data/swr_auth_to_auth_nodes_20222208_fake_demographics.csv")

external_stylesheets = ['assets/style.css']

layout = html.Div([

  # HEADER #
  create_row(
    html.Header(
    [
      html.Div(
      html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),className="banner_logo_not_home")
      ),
      html.Div([
        html.H2("Basic Summary of the Corpus"),
        html.P(
            "This page is for demonstration purposes only. Currently using generated race and gender identity data with original data. Names are removed from the data that is integrated with the fake identity data.",
            className="disclaimer"
        ),
      ]),
    ], 
    className="heatmap_header",
    id="header_banner")
  ),
  create_row([
    html.Section([
      html.H2("Top Cited Scholars"),
      html.Figure([
        html.Img(
          src="assets/images/swr-line-top25-overall-all-years.png"
        ),
        html.Figcaption("Figure 1. Top 25 cited scholars overall across all years."),
      ],className="")
    ], className="max_width__vw_70")
  ]),
  # SELECTION AREA #
  create_row(
    html.Section([
      html.H2("Scholar Identities Across All Journals"),
      html.P(
        "In this section, explore authors' identity across the discipline's journals. Use the slider at the bottom to adjust what years are displayed."
      ),
      html.Hr(),
      html.P("Choose citation module of interest among the Top 20:"),
      
      html.Div(html.Div([
        dcc.Dropdown(
          id='module-type',
          clearable=False,
          value=1,
          options=[
            {'label': x, 'value': x} for x in df["module_id"].unique()
          ]),
      ],className="two columns kws__dropdown_label"), className="row kws__dropdown_row"),

      html.Div(
        id="output-div",
        children=[]
      ),
    ],className="max_width__vw_80"),
  ),

])


@callback(
  Output(component_id="output-div", component_property="children"),
  Input(component_id="module-type", component_property="value"),
)
def make_graphs(module_chosen):
  
  # HISTOGRAM RACE
  df_hist_race = df[df["module_id"]==module_chosen]
  fig_hist_race = px.histogram(df_hist_race, x="node_race")
  fig_hist_race.update_xaxes(categoryorder="total descending")

  # STRIP CHART - RACE
  fig_strip_race = px.strip(
                df_hist_race,
                x="node_flow_score",
                y="node_gender_identity")

  # SUNBURST
  fig_sunburst_race = px.sunburst(df, path=["module_id", "node_race", "node_gender_identity"])

  # Empirical Cumulative Distribution
  fig_ecdf_gender = px.ecdf(df, x="node_race", color="module_id")

  # LINE CHART
  # df_line = df.sort_values(by=["intake_time"], ascending=True)
  
  # df_line = df_line.groupby(
  #     ["intake_time", "module_id"]).size().reset_index(name="count")
  
  # fig_line = px.line(df_line,
  #                     x="intake_time",
  #                     y="count",
  #                     color="module_id", markers=True)

  return [
    html.Div([
        html.Div([dcc.Graph(figure=fig_hist_race)], className="six columns", style={"flex": "1 1 300px"}),
        html.Div([dcc.Graph(figure=fig_strip_race)], className="six columns", style={"flex": "1 1 300px"}),
    ], className="row", style={"flex-wrap":"wrap","margin":"1em"}),
    html.H2("Top 20 Modules", style={"textAlign":"center"}),
    html.Hr(),
    # SUNBURST
    html.Div([
      html.H3("Module Composition by Race and Gender Identity", style={"textAlign":"center", "margin-left": "25px","font-size":"1.25rem"}),
      html.Div(
        [dcc.Graph(figure=fig_sunburst_race)],
        className="fig_sunburst_race twelve columns",
        style={
          "flex":"1 1 100vw",
          "width": "100%",
          "height": "100vh"
      }),
    ], className="row", style={"width": "100%","height": "100vh"}),
    # CUMULATIVE DISTRIBUTION LINE
    html.Div([
      html.H3("Empirical Cumulative Distribution of Gender Identity", style={"textAlign":"center", "margin-left": "25px","font-size":"1.25rem"}),
      html.Div(
        [dcc.Graph(figure=fig_ecdf_gender)],
        className="fig_ecdf_gender twelve columns",
        style={
          "flex":"1 1 100vw",
          "width": "100%",
          "height": "100vh"
      }),
    ], className="row", style={"width": "100%","height": "100vh"}),
    # html.Div([
    #     html.Div([dcc.Graph(figure=fig_line)], className="twelve columns"),
    # ], className="row"),
  ]