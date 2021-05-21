import dash_core_components as dcc
import dash_html_components as html

from .components import (
    cards,
    filters,
    footer,
    header,
    page_header,
    tab_dashboard,
    tab_data,
    tab_map,
)


def layout(data, all_data):
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
