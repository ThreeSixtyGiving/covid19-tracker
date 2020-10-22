import dash_core_components as dcc
import dash_html_components as html


def tab_map(data, all_data):
    return dcc.Tab(
        label="Map",
        value="map",
        className="",
        selected_className="",
        children=[
            html.Div(
                id="geomap-container", children=[]
            ),
        ],
    )
