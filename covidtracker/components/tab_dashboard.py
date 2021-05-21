import dash_core_components as dcc
import dash_html_components as html

from covidtracker.components import chart


def tab_dashboard(data, all_data):
    return dcc.Tab(
        label="Dashboard",
        value="dashboard",
        className="",
        selected_className="",
        children=[
            html.Div(
                className="grid grid--two-columns",
                children=[
                    html.Div(
                        id="data-chart",
                        className="grid__all",
                        children=[
                            chart(data["grants"]),
                        ],
                    ),
                    html.Div(
                        className="grid__1",
                        children=[
                            dcc.Markdown(
                                """
        Grants are included if the use the terms "covid", "coronavirus",
        "pandemic" or "cv19" somewhere in the grant description, title,
        classification or grant programme.

        This data is based on UK foundations reporting grants using the
        [360Giving Data Standard](http://standard.threesixtygiving.org/en/latest/). It only includes grants awarded in
        British Pounds that have already been made (rather than amounts
        committed to grant programmes).
    """
                            )
                        ],
                    ),
                    html.Div(
                        className="grid__1",
                        children=[
                            dcc.Markdown(
                                """
        Not all foundations publish their grants as open data, and some
        publishers do not immediately publish their latest data.

        Some of the data includes grants made to other grantmakers to distribute. You can choose to exclude
        these grants from the analysis to prevent double counting.
    """
                            ),
                            dcc.Markdown(
                                """
        For more information please contact [labs@threesixtygiving.org](mailto:labs@threesixtygiving.org).
    """
                            ),
                        ],
                    ),
                    html.Div(
                        id="top-funders",
                        className="",
                        children=[],
                    ),
                    html.Div(
                        id="award-amount",
                        className="",
                        children=[],
                    ),
                    html.Div(
                        id="regions-chart",
                        className="",
                        children=[],
                    ),
                    html.Div(
                        id="organisation-type",
                        className="",
                        children=[],
                    ),
                    html.Div(
                        id="organisation-size",
                        className="",
                        children=[],
                    ),
                    html.Div(
                        id="word-cloud",
                        className="grid__all",
                        children=[],
                    ),
                ],
            ),
        ],
    )
