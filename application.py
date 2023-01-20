import dash
import dash_bootstrap_components as dbc

application = dash.Dash(
    __name__,
    title="SWR Dashboard",
    # plugins=[dl.plugins.pages],
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    use_pages=True,
    suppress_callback_exceptions=True,
)

# Declare server for Heroku deployment. Needed for Procfile.
server = application.server

navbar = dbc.NavbarSimple(
    dbc.DropdownMenu(
        [
            dbc.DropdownMenuItem(page["name"], href=page["path"])
            for page in dash.page_registry.values()
            if page["module"] != "pages.not_found_404"
        ],
        nav=True,
        label="Data View Menu",
    ),
    brand="SWR Citational Politics Dashboard",
    dark=True,
    className="mb-2",
    id="main_nav",
)

application.layout = dbc.Container(
    [
        navbar,
        dash.page_container,
    ],
    fluid=True,
)

if __name__ == "__main__":
    application.run(debug=True)
    # application.run_server(debug=True)
    # application.run_server(
    #     host='0.0.0.0',
    #     port=8080,
    #     debug=False,
    #     use_reloader=False)
