import os
import pandas as pd
import dash             #(version 1.8.0 / 2.6.1)
import dash_bootstrap_components as dbc
import plotly as px
import base64
from dash_extensions.enrich import dash_table, dcc, html, callback
from dash.dependencies import Input, Output
from .lib.network_data.network_functions import create_row

dash.register_page(
  __name__,
  name="Explore Module Data Table",
  order=2,
  title="Explore Module Table"
)

data_dir = os.path.abspath('./data')
this_dir_img, _ = os.path.split(__file__)
image_filename = os.path.join(this_dir_img, "lib/assets", "cccc_logo.jpeg")
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

#---------------------------------------------------------------
# Import Data
df = pd.read_csv(data_dir+"/per_module_aggregated_scores_counts.csv")

layout = html.Div([
    dash_table.DataTable(
        id='datatable-row-ids',
        columns=[
            {'name': i, 'id': i, 'deletable': True} for i in df.columns
            # omit the id column
            if i != 'id'
        ],
        data=df.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode='multi',
        row_selectable='multi',
        row_deletable=True,
        selected_rows=[],
        page_action='native',
        page_current= 0,
        page_size= 10,
    ),
    html.Div(id='datatable-row-ids-container')
])

@callback(
    Output('datatable-row-ids-container', 'children'),
    Input('datatable-row-ids', 'derived_virtual_row_ids'),
    Input('datatable-row-ids', 'selected_row_ids'),
    Input('datatable-row-ids', 'active_cell'))
def update_table_graphs(row_ids, selected_row_ids, active_cell):
  # When the table is first rendered, `derived_virtual_data` and
  # `derived_virtual_selected_rows` will be `None`. This is due to an
  # idiosyncrasy in Dash (unsupplied properties are always None and Dash
  # calls the dependent callbacks when the component is first rendered).
  # So, if `rows` is `None`, then the component was just rendered
  # and its value will be the same as the component's dataframe.
  # Instead of setting `None` in here, you could also set
  # `derived_virtual_data=df.to_rows('dict')` when you initialize
  # the component.
  selected_id_set = set(selected_row_ids or [])

  if row_ids is None:
      dff = df
      # pandas Series works enough like a list for this to be OK
      row_ids = df['module_id']
  else:
      dff = df.loc[row_ids]

  active_row_id = active_cell['row_id'] if active_cell else None

  colors = ['#FF69B4' if id == active_row_id
            else '#7FDBFF' if id in selected_id_set
            else '#0074D9'
            for id in row_ids]

  return [
      dcc.Graph(
          id=column + '--row-ids',
          figure={
              'data': [
                  {
                      'x': dff['id'],
                      'y': dff[column],
                      'type': 'bar',
                      'marker': {'color': colors},
                  }
              ],
              'layout': {
                  'xaxis': {'automargin': True},
                  'yaxis': {
                      'automargin': True,
                      'title': {'text': column}
                  },
                  'height': 250,
                  'margin': {'t': 10, 'l': 10, 'r': 10},
              },
          },
      )
      # check if column exists - user may have deleted it
      # If `column.deletable=False`, then you don't
      # need to do this check.
      for column in ['id', 'module_id', 'race', 'gender_identity', 'sexual_identity', 'flow_mean', 'flow_median', 'flow_max', 'count'] if column in dff
  ]