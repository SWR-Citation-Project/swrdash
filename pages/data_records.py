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
  name="Explore Full Network Data Table",
  order=2,
  title="Explore Full Network Data Table"
)

data_dir = os.path.abspath('./data')
this_dir_img, _ = os.path.split(__file__)
image_filename = os.path.join(this_dir_img, "lib/assets", "cccc_logo.jpeg")
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

#---------------------------------------------------------------
# Import Data
df = pd.read_csv(data_dir+"/swr_auth_to_auth_edgelist_20222208.csv")


# add an id column and set it as the index
# in this case the unique ID is just the country name, so we could have just
# renamed 'edge_id' to 'id' (but given it the display name 'country'), but
# here it's duplicated just to show the more general pattern.
df['id'] = df['edge_id']

df.set_index('id', inplace=True, drop=False)

columns_list = list(df.columns)

#---------------------------------------------------------------
# Layout for Page

layout = html.Div([
    # HEADER
    create_row(
        html.Header(
            [
                html.Div(
                    html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), width="80px")
                ),
                html.Div(
                [
                    html.H2("Full Edge List"),
                    html.P(
                    "(For demonstration purposes only. Currently using generated race data with original data.)",
                    className="disclaimer"
                    ),
                    html.P(
                    "Explore published authors across the discipline's journals by race. Use the left-side panel to filter and modify the network diagram."
                    )
                ])
            ], 
            className="network_header",
            id="header_banner"
        )
    ),
    # EXPORT DATA BUTTONS
    html.Div(
        [
            html.Button("Download as CSV", id="records_btn_csv"),
            dcc.Download(id="download-dataframe-csv"),
        ]
    ),

    html.Div([
        html.Div(id='graph1', children=[], className='six columns'),
    ], className='row'),

    dash_table.DataTable(
        id='datatable-row-ids',
        columns=[
            {'name': i, 'id': i, 'deletable': True} for i in df.columns
            # omit the id column
            if i != 'id'
        ],
        data=df.to_dict('records'),
        editable=True,
        style_table={
            'overflowX': 'auto'
        },
        style_data={
            'color': 'black',
            'backgroundColor': 'white'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(220, 220, 220)',
            }
        ],
        style_header={
            'backgroundColor': 'rgb(210, 210, 210)',
            'color': 'black',
            'fontWeight': 'bold'
        },
        style_cell={
            'textAlign': 'left',
        },
        filter_action="native",
        sort_action="native",
        sort_mode='multi',
        row_selectable='multi',
        row_deletable=True,
        selected_rows=[],
        page_action='native',
        page_current= 0,
        page_size= 15,
    ),
    html.Div(id='datatable-row-ids-container'),

    # dcc.Store inside the user's current browser session
    # dcc.Store(id='store-data', data=[], storage_type='memory') # 'local' or 'session'
])

@callback(
    Output('download-dataframe-csv', 'data'),
    Input('records_btn_csv', 'n_clicks'),
    prevent_initial_call=True,
)
def export_as_csv(n_clicks):
    return dcc.send_data_frame(df.to_csv, 'full_swr_edgelist_2011_2019.csv')

@callback(
    Output('datatable-row-ids-container', 'children'),
    Input('datatable-row-ids', 'derived_virtual_row_ids'),
    Input('datatable-row-ids', 'selected_row_ids'),
    Input('datatable-row-ids', 'active_cell'))
def update_graphs(row_ids, selected_row_ids, active_cell):
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
        row_ids = df['id']
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
                        'x': dff['edge_id'],
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
        for column in columns_list if column in dff
    ]

# @callback(
#     Output('store-data', 'data'),
#     Input('data-set-chosen', 'value')
# )
# def store_data(value):
#     print(value)
#     # hypothetical enormous dataset with millions of rows
#     if value == 'full_edge_list':
#         dataset = pd.read_csv("./data/network/swr_auth_to_auth_edgelist_20222208.csv")
#         print(dataset.head(5))
#     # elif value == 'tips':
#     #     dataset = px.data.tips()
#     # elif value == 'iris':
#     #     dataset = px.data.iris()
#         return dataset.to_dict('records')
#     # 2. or save as string like JSON
#     # return dataset.to_json(orient='split')


@callback(
    Output('graph1', 'children'),
    Input('datatable-row-ids', 'derived_virtual_row_ids')
)
def create_graph1(row_ids):

    dff = df.loc[row_ids]
    
    print(dff.head())
    print(type(dff))

    fig1 = px.line(dff, x='target_module_id', y='target_flow_score', color='continent')
    return dcc.Graph(figure=fig1)


# @callback(
#     Output('table-placeholder', 'children'),
#     Input('store-data', 'data')
# )
# def create_graph1(data):
#     print('here')
#     dff = pd.DataFrame(data)
#     # 2. convert string like JSON to pandas dataframe
#     # dff = pd.read_json(data, orient='split')
#     my_table = dash_table.DataTable(
#         columns=[{"name": i, "id": i} for i in dff.columns],
#         data=dff.to_dict('records')
#     )
#     return my_table