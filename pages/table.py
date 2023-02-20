import os
import pandas as pd
import dash #(version 1.8.0 / 2.6.1)
import base64
from dash import dash_table, dcc, html, callback
from dash.dependencies import Input, Output
from .lib.network_data.network_functions import create_row

dash.register_page(
  __name__,
  name="Tabulated Top 20 Modules",
  order=4,
  title="Tabulated Top 20 Modules"
)

data_dir = os.path.abspath('./data')
this_dir_img, _ = os.path.split(__file__)
image_filename = os.path.join(this_dir_img, "lib/assets", "cccc_logo.jpeg")
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

#---------------------------------------------------------------
# Import Data
df = pd.read_csv(data_dir+"/per_module.csv")

external_stylesheets = ['assets/style.css']

dropdown_options = [
    'per_module.csv',
    'per_race.csv',
    'per_gender_identity.csv',
    'per_sexual_identity.csv'
]

layout = html.Div([
    # HEADER #
    create_row(
        html.Header(
        [
            html.Div(
            html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),className="banner_logo_not_home")
            ),
            html.Div(
            [
            html.H2("Explore Aggregated Data Among the Top 20 Citation Modules"),
            html.P(
                "This page is for demonstration purposes only. Currently using generated race, gender identity, and sexual identity data with original data. Names are removed from the data set.",
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
    html.Section([
        html.H2("Summary Charts from Table"),
        html.Div(
            id='datatable-row-ids-container',
            className="grid__charts_parent",
        ),
    ]),
    html.Section([
        html.Div([
            html.P("Select a Different Data Set: "),
            html.Div([dcc.Dropdown(
                id="field_dropdown",
                options=[{
                    'label': i,
                    'value': i
                } for i in dropdown_options],
                value='per_module.csv')],
                style={'width': '100%','display': 'inline-block'}
            )
        ],className="selection__flex_parent"),
        dash_table.DataTable(
            id='datatable-row-ids',
            columns=[
                {'name': i, 'id': i, 'deletable': False} for i in df.columns
                # omit the id column
                if i != 'id'
            ],
            data=df.to_dict('records'),
            editable=False,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            column_selectable="single",
            row_selectable="multi",
            row_deletable=False,
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current= 0,
            page_size= 20,
        )
    ],className="selection__prompt")
])

@callback(
    Output('datatable-row-ids', 'data'),
    [Input('field_dropdown', 'value')])
def update_datatable(user_selection):
    new_path = data_dir+'/'+user_selection
    return pd.read_csv(new_path).to_dict('records')

@callback(
    Output('datatable-row-ids', 'columns'),
    [Input('field_dropdown', 'value')])
def update_table_cols(user_selection):
    new_path = data_dir+'/'+user_selection
    coldf = pd.read_csv(new_path)
    new_cols = [ {'name': i, 'id': i, 'deletable': True} for i in coldf.columns
            # omit the id column
            if i != 'id'
        ]
    return new_cols

@callback(
    Output('datatable-row-ids-container', 'children'),
    Input('datatable-row-ids', 'data'),
    Input('datatable-row-ids', 'derived_virtual_row_ids'),
    Input('datatable-row-ids', 'selected_row_ids'),
    Input('datatable-row-ids', 'active_cell'))
def update_table_graphs(data_dict, row_ids, selected_row_ids, active_cell):

    ### UPDATE BASED ON SELECTED DATA SET ###
    # Set data for table and charts
    data = pd.DataFrame(data_dict)
    # Set row ID
    selected_id_set = set(selected_row_ids or [])
    # Set list of columns
    _col_list = list(data.columns)[2:]
    _id = list(data.columns)[1]

    if row_ids is None:
        the_id = list(data.columns)[1]
        # pandas Series works enough like a list for this to be OK
        row_ids = data[the_id]
    else:
        data = data.loc[row_ids]

    active_row_id = active_cell['row_id'] if active_cell else None

    # Sets highlighted colors based on selected cell in row
    colors = ['#FF69B4' if id == active_row_id
            else '#7FDBFF' if id in selected_id_set
            else '#0074D9'
            for id in row_ids]

    # Generate charts
    return [
        dcc.Graph(
            id=column + '--row-ids',
            className="grid__chart_child",
            figure={
                'data': [
                    {
                        'x': data[_id],
                        'y': data[column],
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
        for column in _col_list if column in data
    ]