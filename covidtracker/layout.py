from dash import dcc, html

from covidtracker.components import (
    cards,
    filters,
    footer,
    header,
    page_header,
    tab_dashboard,
    tab_data,
    tab_map,
)
from covidtracker.data import filter_data, get_data


def layout():
    all_data = get_data()
    if all_data["grants"] is None:
        return html.Div("No data found")
    data = filter_data(all_data)
    return html.Div(
        id="main-div",
        className="layout layout--single-column layout--full",
        children=[
            dcc.Location(id="url", refresh=False),
            dcc.Store(id="filters"),
            header(),
            html.Main(
                className="layout__content",
                children=[
                    html.Div(
                        className="layout__content-inner wrapper",
                        children=[
                            html.Div(
                                id="page-header",
                                className="grid grid--one-column",
                                children=page_header(data),
                            ),
                            html.Div(id="data-cards", children=cards(data["grants"])),
                            html.Div(className="spacer-5"),
                            html.Div(
                                className="", children=filters(data["all_grants"])
                            ),
                            dcc.Loading(
                                id="data-tab-loading",
                                debug=False,
                                fullscreen=False,
                                color="#bc2c26",
                                type="dot",
                                children=[
                                    dcc.Tabs(
                                        parent_className="",
                                        id="tabs",
                                        value="dashboard",
                                        className="filters",
                                        children=[
                                            tab_dashboard(data, all_data),
                                            tab_map(data, all_data),
                                            tab_data(data, all_data),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # subscribe(),
            footer(),
        ],
    )
