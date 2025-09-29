from dash import dcc, html


def tab_map(data, all_data):
    return dcc.Tab(
        label="Map",
        value="map",
        className="",
        selected_className="",
        children=[
            html.Div(id="geomap-container", children=[]),
        ],
    )
