import os
import visdcc
import base64
import dash
import pandas as pd
from dash import html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from .lib.network_data.network_functions import get_options, fetch_flex_row_style, create_row, get_select_form_layout, _callback_search_graph, _callback_size_edges, _callback_color_edges, _callback_size_nodes, _callback_color_nodes, _callback_filter_edges, _callback_filter_nodes, get_numerical_features, get_color_popover_legend_children, get_categorical_features
from .lib.network_data.parse_dataframe import parse_dataframe

dash.register_page(
  __name__,
  name="Publisher-Race Network",
  order=4,
  title="Publisher-Race Network"
)
# ----------------------------
# Load Data & Prep Data
# ----------------------------
this_dir, _ = os.path.split(__file__)

__edge_filename__ = 'swr-edges-pub-to-mmu.csv'
__node_filename__ = 'swr-nodes-mmu.csv'

edge_df_data = pd.read_csv(os.path.join(
    this_dir, 'lib/network_data', __edge_filename__))
node_df_data = pd.read_csv(os.path.join(
    this_dir, 'lib/network_data', __node_filename__))

edge_df, node_df = edge_df_data, node_df_data

node_columns = list(node_df.columns)
edge_columns = list(edge_df.columns)
list_pubs = list(edge_df['from'].drop_duplicates(keep='first'))

# ----------------------------
# Create Copy for Filter Hints
# ----------------------------
node_copy = 'Filter nodes with the following column names: '
index = 0
node_length = len(node_columns)
for node in node_columns:

  if index < node_length-1:

    node_copy = node_copy + node + ', '

    index = index + 1
  
  else:

    node_copy = node_copy + 'or ' + node + '.'

edge_copy = 'Filter edges with the following column names: '
edge_index = 0
edge_length = len(edge_columns)
for edge in edge_columns:

  if edge_index < edge_length-1:

    edge_copy = edge_copy + edge + ', '

    edge_index = edge_index + 1
  
  else:

    edge_copy = edge_copy + 'or ' + edge + '.'

data, scaling_vars = parse_dataframe(edge_df, node_df)

filtered_data = data.copy()

node_value_color_mapping = {}
edge_value_color_mapping = {}
directed = True
vis_opts = None

# Create layout
this_dir, _ = os.path.split(__file__)
image_filename = os.path.join(this_dir, "lib/assets", "cccc_logo.jpeg")
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

# ----------------------------
# Layout Functions
# Constants
# --------------
# default node and edge size
DEFAULT_NODE_SIZE = 7
DEFAULT_EDGE_SIZE = 1

# default node and egde color
DEFAULT_COLOR = '#d30348'

# Taken from https://stackoverflow.com/questions/470690/how-to-automatically-generate-n-distinct-colors
KELLY_COLORS_HEX = [
    "#FFB300",  # Vivid Yellow
    "#803E75",  # Strong Purple
    "#FF6800",  # Vivid Orange
    "#A6BDD7",  # Very Light Blue
    "#C10020",  # Vivid Red
    "#CEA262",  # Grayish Yellow
    "#817066",  # Medium Gray

    # The following don't work well for people with defective color vision
    "#007D34",  # Vivid Green
    "#F6768E",  # Strong Purplish Pink
    "#00538A",  # Strong Blue
    "#FF7A5C",  # Strong Yellowish Pink
    "#53377A",  # Strong Violet
    "#FF8E00",  # Vivid Orange Yellow
    "#B32851",  # Strong Purplish Red
    "#F4C800",  # Vivid Greenish Yellow
    "#7F180D",  # Strong Reddish Brown
    "#93AA00",  # Vivid Yellowish Green
    "#593315",  # Deep Yellowish Brown
    "#F13A13",  # Vivid Reddish Orange
    "#232C16",  # Dark Olive Green
]

DEFAULT_OPTIONS = {
    'id': 'pub-to-race',
    'height': '720px',
    'width': '100%',
    'interaction': {'hover': True},
    # 'edges': {'scaling': {'min': 1, 'max': 5}},
    'layout': {'name': 'breadthfirst'},
    'physics': {
        'stabilization': {'iterations': 100},
        'repulsion': {
            'centralGravity': 0.001,
            'springLength': 600,
          'springConstant': 0.05,
          'nodeDistance': 2000,
          'damping': 0.09
        },
    }
}

# Code
# ---------
search_form = dbc.FormGroup(
    [
        # dbc.Label("Search", html_for="search_graph"),
        dbc.Input(type="search", id="search_graph",
                  placeholder="Search node in graph..."),
        dbc.FormText(
            "Show the node you are looking for",
            color="secondary",
        ),
    ]
)

filter_node_form = dbc.FormGroup([
    # dbc.Label("Filter nodes", html_for="filter_nodes"),
    dbc.Textarea(id="filter_nodes",
                 placeholder="Ex. id == 'Black'"),
    dbc.FormText(
        html.P([
            "Filter on node properties by using ",
            html.A("Pandas Query syntax",
                   href="https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html",
                   target="_blank",
                   rel="noopenner"
            ),
            ". Example: id == 'Black'",
        ]),
        color="secondary",
    ),
])

filter_edge_form = dbc.FormGroup([
    dbc.Label("Filter edges", html_for="filter_edges"),
    dbc.Textarea(id="filter_edges",
                 placeholder="Ex. weight > 500"),
    dbc.FormText(
        html.P([
            "Filter on edge properties by using ",
            html.A("Pandas Query syntax",
                   href="https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html",
                   target="_blank",
                   rel="noopenner"
            ),
            ". Example: from == 'CCC', to == 'Black', or weight > 500",
        ]),
        color="secondary",
    ),
])

color_legends = []
color_legends = get_color_popover_legend_children(node_value_color_mapping, edge_value_color_mapping)

# Find categorical features of nodes and edges
cat_node_features = get_categorical_features(
    pd.DataFrame(data['nodes']), 20, ['shape', 'label', 'id'])

# from,to,weight,strength
cat_edge_features = get_categorical_features(pd.DataFrame(
    data['edges']).drop(columns=['color']), 20, ['color', 'from', 'to', 'id']
)

# Get numerical features of nodes and edges
num_node_features = get_numerical_features(pd.DataFrame(data['nodes']))
num_edge_features = get_numerical_features(pd.DataFrame(data['edges']))

"""
  Create and return the layout
"""

layout = html.Div([
  # HEADER
  create_row(
    html.Header(
      [
        html.Div(
          html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), className="banner_logo_not_home")
        ),
        html.Div(
        [
          html.H2("2012 - 2019 Publisher-to-Race Network"),
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
      id="header_banner")
  ),

  # SETTING PANEL
  create_row([
    dbc.Col([
      # setting panel
      dbc.Form([
          # ---- search section ----
          html.H6("Search"),
          html.Hr(className="my-2"),
          search_form,

          # ---- filter section ----
          create_row([
              html.H6("Filter"),
              dbc.Button("Hide/Show", id="filter-show-toggle-button",
                          outline=True, color="secondary", size="sm"),  # legend
            ], {**fetch_flex_row_style(), 'margin-left': 0, 'margin-right': 0, 'justify-content': 'space-between'}
          ),
          dbc.Collapse([
              html.Hr(className="my-2"),
              filter_node_form,
              filter_edge_form,
          ], id="filter-show-toggle", is_open=False),

          # ---- color section ----
          create_row([
              html.H6("Color"),  # heading
              html.Div([
                  dbc.Button("Hide/Show", id="color-show-toggle-button",
                              outline=True, color="secondary", size="sm"),
              ]),
              # add the legends popup
              dbc.Popover(
                  children=color_legends,
                  id="color-legend-popup", is_open=False, target="color-legend-toggle",
              ),
          ], {**fetch_flex_row_style(), 'margin-left': 0, 'margin-right': 0, 'justify-content': 'space-between'}),
          dbc.Collapse([
              html.Hr(className="my-2"),
              get_select_form_layout(
                  id='color_nodes',
                  options=[{'label': opt, 'value': opt}
                            for opt in cat_node_features],
                  label='Color nodes by',
                  description='Select the categorical node property to color nodes by'
              ),
              get_select_form_layout(
                  id='color_edges',
                  options=[{'label': opt, 'value': opt}
                            for opt in cat_edge_features],
                  label='Color edges by',
                  description='Select the categorical edge property to color edges by'
              ),
          ], id="color-show-toggle", is_open=True),

          # ---- size section ----
          create_row([
              html.H6("Size"),  # heading
              dbc.Button("Hide/Show", id="size-show-toggle-button",
                          outline=True, color="secondary", size="sm"),  # legend
              dbc.Button("Legends", id="color-legend-toggle", outline=True, color="secondary", size="sm"), # legend
              # add the legends popup
              dbc.Popover(
                  children=color_legends,
                  id="color-legend-popup", is_open=False, target="color-legend-toggle",
              ),
          ], {**fetch_flex_row_style(), 'margin-left': 0, 'margin-right': 0, 'justify-content': 'space-between'}),
          dbc.Collapse([
              html.Hr(className="my-2"),
              get_select_form_layout(
                  id='size_nodes',
                  options=[{'label': opt, 'value': opt}
                            for opt in num_node_features],
                  label='Size nodes by',
                  description='Select the numerical node property to size nodes by'
              ),
              get_select_form_layout(
                  id='size_edges',
                  options=[{'label': opt, 'value': opt}
                            for opt in num_edge_features],
                  label='Size edges by',
                  description='Select the numerical edge property to size edges by'
              ),
          ], id="size-show-toggle", is_open=True),

      ], className="card", style={'padding': '5px', 'background': '#e5e5e5'}),
      ], width=3, style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),

    # NETWORK GRAPH CANVAS
    dbc.Col(
      visdcc.Network(
          id='pub-to-race-network',
          data=data,
          options=get_options(DEFAULT_OPTIONS, directed)),
      width=9)
  ])
])

# create callbacks to toggle legend popover
@callback(
    Output("color-legend-popup", "is_open"),
    [Input("color-legend-toggle", "n_clicks")],
    [State("color-legend-popup", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open

# create callbacks to toggle hide/show sections - FILTER section
@callback(
    Output("filter-show-toggle", "is_open"),
    [Input("filter-show-toggle-button", "n_clicks")],
    [State("filter-show-toggle", "is_open")],
)
def toggle_filter_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# create callbacks to toggle hide/show sections - COLOR section
@callback(
    Output("color-show-toggle", "is_open"),
    [Input("color-show-toggle-button", "n_clicks")],
    [State("color-show-toggle", "is_open")],
)
def toggle_filter_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# create callbacks to toggle hide/show sections - COLOR section
@callback(
    Output("size-show-toggle", "is_open"),
    [Input("size-show-toggle-button", "n_clicks")],
    [State("size-show-toggle", "is_open")],
)
def toggle_filter_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# create the main callbacks
@callback(
    [Output('pub-to-race-network', 'data'), Output('color-legend-popup', 'children')],
    [Input('search_graph', 'value'),
     Input('filter_nodes', 'value'),
     Input('filter_edges', 'value'),
     Input('color_nodes', 'value'),
     Input('color_edges', 'value'),
     Input('size_nodes', 'value'),
     Input('size_edges', 'value')],
    [State('pub-to-race-network', 'data')]
)
def setting_pane_callback(search_text, filter_nodes_text, filter_edges_text, color_nodes_value, color_edges_value, size_nodes_value, size_edges_value, data):

  # fetch the id of option which triggered
  ctx = dash.callback_context

  # if its the first call
  if not ctx.triggered:

    node_value_color_mapping = {}
    edge_value_color_mapping = {}

    return [
      data, 
      get_color_popover_legend_children(node_value_color_mapping, edge_value_color_mapping)
    ]

  else:

    # find the id of the option which was triggered
    input_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # perform operation in case of search graph option
    if input_id == "search_graph":

      data = _callback_search_graph(data, search_text)
    
    # In case filter nodes was triggered
    elif input_id == 'filter_nodes':

      data = _callback_filter_nodes(data, filter_nodes_text)
    
    # In case filter edges was triggered
    elif input_id == 'filter_edges':

      data = _callback_filter_edges(data, filter_edges_text)
    
    # If color node text is provided
    if input_id == 'color_nodes':

      data, node_value_color_mapping = _callback_color_nodes(color_nodes_value, data, DEFAULT_COLOR, KELLY_COLORS_HEX, filtered_data)
    
    # If color edge text is provided
    if input_id == 'color_edges':

      data, edge_value_color_mapping = _callback_color_edges(color_edges_value, data, DEFAULT_COLOR, KELLY_COLORS_HEX, filtered_data)
    
    # If size node text is provided
    if input_id == 'size_nodes':
      data = _callback_size_nodes(size_nodes_value, data, DEFAULT_NODE_SIZE, scaling_vars, filtered_data)
    
    # If size edge text is provided
    if input_id == 'size_edges':
      data = _callback_size_edges(size_edges_value, data, DEFAULT_EDGE_SIZE, scaling_vars, filtered_data)

  # create the color legend childrens
  color_popover_legend_children = get_color_popover_legend_children(node_value_color_mapping={}, edge_value_color_mapping={})

  # finally return the modified data
  return [data, color_popover_legend_children]
