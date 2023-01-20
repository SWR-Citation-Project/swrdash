import pandas as pd
from dash import html
import dash_bootstrap_components as dbc

def get_options(DEFAULT_OPTIONS, directed):

  opts = DEFAULT_OPTIONS.copy()

  opts['edges'] = {'arrows': {'to': directed}}

  if DEFAULT_OPTIONS is not None:

      opts.update(DEFAULT_OPTIONS)

  return opts

def get_distinct_colors(KELLY_COLORS_HEX, n):
  """Return distict colors, currently atmost 20

  Parameters
  -----------
  n: int
      the distinct colors required
  """
  if n <= 20:
      return KELLY_COLORS_HEX[:n]

def create_card(id, value, description):
  """Creates card for high level stats

  Parameters
  ---------------
  """
  return dbc.Card(
      dbc.CardBody(
          [
              html.H4(id=id, children=value, className='card-title'),
              html.P(children=description),
          ]))

def create_color_legend(text, color):
    """Individual row for the color legend
    """
    return create_row([
        html.Div(style={'width': '10px', 'height': '10px',
                 'background-color': color}),
        html.Div(text, style={'padding-left': '10px'}),
    ])

def fetch_flex_row_style():
    return {'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center', 'align-items': 'center'}

def create_row(children, style=fetch_flex_row_style()):
    return dbc.Row(
                    children,
                    style=style,
                    className="column flex-display"
                  )

def create_network_row(children, style=fetch_flex_row_style()):
    return dbc.Row(
                    children,
                    style=style,
                    className="column flex-display network-flex-container"
                  )

def get_select_form_layout(id, options, label, description):
    """Creates a select (dropdown) form with provides details

    Parameters
    -----------
    id: str
        id of the form
    options: list
        options to show
    label: str
        label of the select dropdown bar
    description: str
        long text detail of the setting
    """
    return dbc.FormGroup([
        dbc.InputGroup([
            dbc.InputGroupAddon(label, addon_type="append"),
            dbc.Select(id=id,
                       options=options
                       ), ]),
        dbc.FormText(description, color="secondary",), ])

def get_categorical_features(df_, unique_limit=20, blacklist_features=['shape', 'label', 'id']):
  """Identify categorical features for edge or node data and return their names
  Additional logics: (1) cardinality should be within `unique_limit`, (2) remove blacklist_features
  """
  # identify the rel cols + None
  cat_features = ['None'] + df_.columns[(df_.dtypes == 'object') & (
    df_.apply(pd.Series.nunique) <= unique_limit)].tolist()

  # remove irrelevant cols
  try:
    for col in blacklist_features:
      cat_features.remove(col)
  except:
    pass
  # return
  return cat_features

def get_numerical_features(df_, unique_limit=20):
  """
    Identify numerical features for edge or node data and return their names
  """
  # supported numerical cols
  numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
  # identify numerical features
  numeric_features = ['None'] + \
    df_.select_dtypes(include=numerics).columns.tolist()

  # remove blacklist cols (for nodes)
  try:
    numeric_features.remove('size')
  except:
    pass
  # return
  return numeric_features

def _callback_search_graph(data, search_text):
  """
    Only show the nodes which match the search text
  """

  nodes = data['nodes']

  for node in nodes:

    if search_text not in node['label']:

        node['hidden'] = True

    else:

        node['hidden'] = False

  data['nodes'] = nodes

  return data


def _callback_filter_nodes(data, filter_nodes_text):
  """Filter the nodes based on the Python query syntax
  """
  filtered_data = data.copy()

  # Listify Comma-Sep Strings
  rm_whitespace_names = filter_nodes_text.strip()
  listify_names = rm_whitespace_names.split(',')

  # Strip each string for good measure
  search_node_name_list = []
  for n in listify_names:
    cn = n.strip().lower()
    search_node_name_list.append(cn)

  print(search_node_name_list)
  
  try:
    nodes = []
    for node in filtered_data['nodes']:
      if node['id'].lower() in search_node_name_list:
        nodes.append(node)
  
    filtered_data['nodes'] = nodes
    data = filtered_data
  
  except:
    data = data
    print("oops wrong node filter query!!")
  
  return data


def _callback_filter_edges(data, filter_edges_text):
  """Filter the edges based on the Python query syntax
  """
  
  filtered_data = data.copy()
  edges_df = pd.DataFrame(filtered_data['edges'])

  try:
  
    edges_list = edges_df.query(filter_edges_text)['id'].tolist()
    edges = []
  
    for edge in filtered_data['edges']:
  
      if edge['id'] in edges_list:
  
        edges.append(edge)
  
    filtered_data['edges'] = edges
    data = filtered_data
  
  except:
  
    data = data
    print("wrong edge filter query!!")
  
  return data


def _callback_color_nodes(color_nodes_value, data, DEFAULT_COLOR, KELLY_COLORS_HEX, filtered_data):
  
  value_color_mapping = {}
  
  # color option is None, revert back all changes
  if color_nodes_value == 'None':
    
    # revert to default color
    for node in data['nodes']:
    
      node['color'] = DEFAULT_COLOR
  
  else:
    
    print("inside color node", color_nodes_value)
    
    unique_values = pd.DataFrame(data['nodes'])[color_nodes_value].unique()
    
    colors = get_distinct_colors(KELLY_COLORS_HEX, len(unique_values))
    
    value_color_mapping = {x: y for x, y in zip(unique_values, colors)}
    
    for node in data['nodes']:
    
      node['color'] = value_color_mapping[node[color_nodes_value]]
  
  # filter the data currently shown
  filtered_nodes = [x['id'] for x in filtered_data['nodes']]
  
  filtered_data['nodes'] = [
  
    x for x in data['nodes'] if x['id'] in filtered_nodes]
  
  data = filtered_data
  
  return data, value_color_mapping


def _callback_size_nodes(size_nodes_value, data, DEFAULT_NODE_SIZE, scaling_vars, filtered_data):

  # color option is None, revert back all changes
  
  if size_nodes_value == 'None':
  
    # revert to default color
  
    for node in data['nodes']:
  
      node['size'] = DEFAULT_NODE_SIZE
  
  else:
  
    print("Modifying node size using ", size_nodes_value)
  
    # fetch the scaling value
    minn = scaling_vars['node'][size_nodes_value]['min']
    maxx = scaling_vars['node'][size_nodes_value]['max']
  
    # define the scaling function
    def scale_val(x): return 20*(x-minn)/(maxx-minn)
  
    # set size after scaling
    for node in data['nodes']:
  
      node['size'] = node['size'] + scale_val(node[size_nodes_value])
  
  # filter the data currently shown
  filtered_nodes = [x['id'] for x in filtered_data['nodes']]
  
  filtered_data['nodes'] = [
  
    x for x in data['nodes'] if x['id'] in filtered_nodes]
  
  data = filtered_data
  
  return data


def _callback_color_edges(color_edges_value, data, DEFAULT_COLOR, KELLY_COLORS_HEX, filtered_data):

  value_color_mapping = {}
  
  # color option is None, revert back all changes
  if color_edges_value == 'None':
  
    # revert to default color
    for edge in data['edges']:
  
      edge['color']['color'] = DEFAULT_COLOR
  
  else:
  
    print("inside color edge", color_edges_value)
  
    unique_values = pd.DataFrame(data['edges'])[color_edges_value].unique()
  
    colors = get_distinct_colors(KELLY_COLORS_HEX, len(unique_values))
  
    value_color_mapping = {x: y for x, y in zip(unique_values, colors)}
  
    for edge in data['edges']:
  
      edge['color']['color'] = value_color_mapping[edge[color_edges_value]]
  
  # filter the data currently shown
  filtered_edges = [x['id'] for x in filtered_data['edges']]
  
  filtered_data['edges'] = [
    x for x in data['edges'] if x['id'] in filtered_edges
  ]
  
  data = filtered_data
  
  return data, value_color_mapping


def _callback_size_edges(size_edges_value, data, DEFAULT_EDGE_SIZE, scaling_vars, filtered_data):
  # color option is None, revert back all changes
  if size_edges_value == 'None':
    # revert to default color
    for edge in data['edges']:
      edge['width'] = DEFAULT_EDGE_SIZE
  else:
    print("Modifying edge size using ", size_edges_value)
    # fetch the scaling value
    minn = scaling_vars['edge'][size_edges_value]['min']
    maxx = scaling_vars['edge'][size_edges_value]['max']
    # define the scaling function
    def scale_val(x): return 20*(x-minn)/(maxx-minn)
    # set the size after scaling
    for edge in data['edges']:
      edge['width'] = scale_val(edge[size_edges_value])
  
  # filter the data currently shown
  filtered_edges = [x['id'] for x in filtered_data['edges']]
  
  filtered_data['edges'] = [
      x for x in data['edges'] if x['id'] in filtered_edges]
  data = filtered_data
  return data


def get_color_popover_legend_children(node_value_color_mapping, edge_value_color_mapping):
  """Get the popover legends for node and edge based on the color setting
  """
  # var
  popover_legend_children = []

  # common function
  def create_legends_for_nodes(title, legend):
    
    # add title
    _popover_legend_children = [dbc.PopoverHeader(f"{title} legends")]
    
    # add values if present
    if len(legend) > 0:
      
      for key, value in legend.items():

        _popover_legend_children.append(
          # dbc.PopoverBody(f"Key: {key}, Value: {value}")
          create_color_legend(key, value)
        )
    else:  # otherwise add filler

      _popover_legend_children.append(dbc.PopoverBody(f"no {title.lower()} colored!"))

    return _popover_legend_children

  def create_legends_for_edges(title, legend):
    
    # add title
    _popover_legend_children = [dbc.PopoverHeader(f"{title} legends")]
    
    # add values if present
    if len(legend) > 0:
      
      for key, value in legend.items():

        _popover_legend_children.append(
          # dbc.PopoverBody(f"Key: {key}, Value: {value}")
          create_color_legend(key, value)
        )
    else:  # otherwise add filler

      _popover_legend_children.append(dbc.PopoverBody(f"no {title.lower()} colored!"))

    return _popover_legend_children

  # add node color legends
  popover_legend_children.extend(create_legends_for_nodes("Node", node_value_color_mapping))

  # add edge color legends
  popover_legend_children.extend(create_legends_for_edges("Edge", edge_value_color_mapping))

  return popover_legend_children

