from dash import dcc, html
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app
from app import server

# Connect to your app pages
from pages import byrace


app.layout = html.Div([
  dcc.Location(id='url', refresh=False),
  html.Div([
      dcc.Link('Journals by Race', href='/pages/byrace'),
  ], className="row"),
  html.Div(id='page-content', children=[])
])


@app.callback(
  Output('page-content', 'children'),
  [Input('url', 'pathname')]
)

def display_page(pathname):
  if pathname == '/pages/byrace':
    return byrace.layout
  if pathname == '/':
      return byrace.layout
  else:
    return "404 Page Error! Please choose a link"


if __name__ == '__main__':

  app.run_server(debug=False)