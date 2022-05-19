import os
import pandas as pd
import dash
import base64
dash.register_page(__name__)
from dash import Dash, dcc, html, Input, Output, callback
from .lib.network_data.network_functions import create_row
import plotly.express as px

import xarray as xr
# Load xarray from dataset included in the xarray tutorial
ds = xr.tutorial.open_dataset('air_temperature').air[:20]
print(ds)

this_dir = os.path.abspath('./data')

this_dir_img, _ = os.path.split(__file__)
image_filename = os.path.join(this_dir_img, "lib/assets", "cccc_logo.jpeg")
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

__file__ = this_dir + '/pub_race_matrix.csv'

df = pd.read_csv(__file__, index_col='Citing Publisher')

'''
    Goal: Use Intra-Percentages to create new values per pub
'''
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

intra_percentages_df = find_intra_percentages(df)

layout = html.Div(
    [
        create_row(
            html.Header(
            [
                html.Div(
                html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), width="80px")
                ),
                html.Div(
                [
                html.H2("2012 - 2019 Publisher-to-Race Heatmap"),
                html.P(
                    "(For demonstration purposes only. Currently using generated race data with original data.)",
                    className="disclaimer"
                ),
                html.P(
                    "Explore published the percentage of authors' race (percentage) across the discipline's journals."
                )
                ]),
            ], 
            className="heatmap_header",
            id="header_banner")
        ),
        html.Div([
            html.P("Filter by racial demographics:", className="filter_prompt"),
            dcc.Checklist(
                id="heatmap-race",
                options=[{"label": x, "value": x} for x in intra_percentages_df.columns],
                value=df.columns.tolist(),
            ),
        ]),
        dcc.Graph(id="heatmaps-graph"),
    ]
)

# Labels for each heatmap cell
cell_copy = []
for cell_values in intra_percentages_df.values.tolist():

    cell_strings = []
    for cv in cell_values:

        cell_strings.append(str(cv))
    
    cell_copy.append(cell_values)

@callback(
    Output("heatmaps-graph", "figure"), 
    Input("heatmap-race", "value")
)
def filter_heatmap(cols):

    fig = px.imshow(
        intra_percentages_df[cols],
        labels = dict(
            x="Racial Demographic", 
            y="Citing Publisher", 
            color="Total Citing by Race (%)"
        ),
        aspect="auto"
    )

    fig.update_xaxes(side="top")

    return fig
