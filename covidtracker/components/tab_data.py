import dash_core_components as dcc
import dash_html_components as html

from covidtracker.components.datasources import datasources
from covidtracker.components.table import table


def tab_data(data, all_data):
    return dcc.Tab(
        label="Data",
        value="data",
        className="",
        selected_className="",
        children=[
            html.Div(
                className="grid grid--two-columns",
                children=[
                    html.Div(
                        className="grid__all",
                        children=[
                            html.Div(
                                [
                                    html.H3(
                                        className="h3",
                                        children="Grants",
                                    ),
                                    html.Div(
                                        className="table table--zebra",
                                        id="data-table",
                                        children=[table(data["grants"])],
                                    ),
                                ]
                            )
                        ],
                    ),
                    html.Div(
                        className="grid__all",
                        children=[
                            dcc.Markdown(
                                """
        [GrantNav](https://grantnav.threesixtygiving.org/) is search-engine
        for grants data. Explore and download in detail on where and how much funding
        goes across billions of pounds of grants.
    """
                            ),
                            html.A(
                                className="button button--orange",
                                href="/data/grants.csv",
                                target="_blank",
                                children="Download all grants (CSV)",
                            ),
                            " ",
                            html.A(
                                className="button button--orange",
                                href="/data/grants.json",
                                target="_blank",
                                children="Download all grants (JSON)",
                            ),
                            " ",
                            html.A(
                                className="button button--orange",
                                href="/data/la.csv",
                                target="_blank",
                                children="Download Local Authority summaries (CSV)",
                            ),
                            " ",
                            html.A(
                                className="button button--orange",
                                href="https://grantnav.threesixtygiving.org/search?json_query=%7B%22query%22%3A+%7B%22bool%22%3A+%7B%22must%22%3A+%7B%22query_string%22%3A+%7B%22query%22%3A+%22coronavirus+OR+pandemic+OR+covid+OR+%5C%22covid19%5C%22%22%2C+%22default_field%22%3A+%22%2A%22%7D%7D%2C+%22filter%22%3A+%5B%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%2C+%22must%22%3A+%7B%7D%2C+%22minimum_should_match%22%3A+1%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%7B%22range%22%3A+%7B%22amountAwarded%22%3A+%7B%7D%7D%7D%2C+%22must%22%3A+%7B%7D%2C+%22minimum_should_match%22%3A+1%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%7B%22range%22%3A+%7B%22awardDate%22%3A+%7B%22format%22%3A+%22year%22%2C+%22gte%22%3A+%222020%7C%7C%2Fy%22%2C+%22lte%22%3A+%222020%7C%7C%2Fy%22%7D%7D%7D%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%5D%7D%7D%2C+%22sort%22%3A+%7B%22_score%22%3A+%7B%22order%22%3A+%22desc%22%7D%7D%2C+%22aggs%22%3A+%7B%22fundingOrganization%22%3A+%7B%22terms%22%3A+%7B%22field%22%3A+%22fundingOrganization.id_and_name%22%2C+%22size%22%3A+50%7D%7D%2C+%22recipientOrganization%22%3A+%7B%22terms%22%3A+%7B%22field%22%3A+%22recipientOrganization.id_and_name%22%2C+%22size%22%3A+3%7D%7D%2C+%22recipientRegionName%22%3A+%7B%22terms%22%3A+%7B%22field%22%3A+%22recipientRegionName%22%2C+%22size%22%3A+3%7D%7D%2C+%22recipientDistrictName%22%3A+%7B%22terms%22%3A+%7B%22field%22%3A+%22recipientDistrictName%22%2C+%22size%22%3A+3%7D%7D%2C+%22currency%22%3A+%7B%22terms%22%3A+%7B%22field%22%3A+%22currency%22%2C+%22size%22%3A+3%7D%7D%7D%2C+%22extra_context%22%3A+%7B%22awardYear_facet_size%22%3A+3%2C+%22amountAwardedFixed_facet_size%22%3A+3%7D%7D",
                                target="_blank",
                                children="Search on GrantNav",
                            ),
                            html.Div(className="spacer-3"),
                            html.P(
                                html.Small(
                                    html.Em(
                                        id="last-updated",
                                        children=[
                                            "Last updated ",
                                            "{:%Y-%m-%d %H:%M}".format(
                                                data["last_updated"]
                                            ),
                                        ],
                                    ),
                                ),
                            ),
                            html.H3(
                                className="h3",
                                children="Data Sources",
                            ),
                            html.Div(
                                className="table table--zebra",
                                id="data-sources",
                                children=[datasources(data["grants"])],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
