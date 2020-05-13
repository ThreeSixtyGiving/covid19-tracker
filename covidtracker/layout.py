import dash_html_components as html
import dash_core_components as dcc
from .components import cards, chart, table, header, footer, subscribe, filters, page_header, wordcloud

def layout(data, all_data):
    return html.Div(
        id="main-div",
        className="layout layout--single-column layout--full",
        children=[
            dcc.Location(id='url', refresh=False),
            dcc.Store(id='filters'),
            header(),
            html.Main(className="layout__content", children=[
                html.Div(className="layout__content-inner", children=[
                    html.Div(id="page-header", className="grid grid--one-column", children=page_header(data)),
                    html.Div(id="data-cards", children=cards(data)),
                    html.Div(className="spacer-3"),
                    html.Div(className="filter-section", children=filters(all_data)),
                    html.Div(className="spacer-3"),
                    html.Div(className="grid grid--two-columns", children=[
                        html.Div(id="data-chart", className="grid__all", children=[
                            chart(data),
                        ]),
                        html.Div(id="word-cloud", className="grid__all", children=[
                            wordcloud(data),
                        ]),
                    ]),
                    html.Div(className="spacer-3"),
                    html.Div(className="grid grid--two-columns", children=[
                        html.Div(className="grid__1", children=[
                            dcc.Markdown('''
                                Grants are included if the use the terms "covid", "coronavirus", 
                                "pandemic" or "cv19" somewhere in the grant description, title,
                                classification or grant programme.

                                This data is based on UK foundations reporting grants using the
                                360Giving Data Standard. It only includes grants awarded in 
                                British Pounds that have already been made (rather than amounts 
                                committed to grant programmes).
                            ''')
                        ]),
                        html.Div(className="grid__1", children=[
                            dcc.Markdown('''
                                Not all foundations publish their grants as open data, and some
                                publishers do not immediately publish their latest data. 

                                Some of the data includes grants made to other grantmakers to distribute. You can choose to exclude
                                these grants from the analysis to prevent double counting.
                            '''),
                            dcc.Checklist(
                                options=[
                                    {'label': 'Don\'t include grants to other grantmakers', 'value': 'exclude'},
                                ],
                                id="doublecount-filter",
                                value=[],
                                inputStyle={
                                    'marginRight': '4px',
                                },
                                labelStyle={
                                    'display': 'inline-block'
                                },
                            ),
                            dcc.Markdown('''
                                For more information please contact [labs@threesixtygiving.org](mailto:labs@threesixtygiving.org).
                            '''),
                        ]),
                    ]),
                    html.Div(className="grid grid--two-columns", children=[
                        html.Div(className="grid__all", children=[
                            html.Div([
                                html.H3(className='h3', children="Grants"),
                                html.Div(className='table table--zebra', id="data-table", children=[
                                    table(data)
                                ])
                            ])
                        ]),
                        html.Div(className="grid__all", children=[
                            dcc.Markdown('''
                                [GrantNav](https://grantnav.threesixtygiving.org/) is search-engine
                                for grants data. Explore and download in detail on where and how much funding 
                                goes across billions of pounds of grants.
                            '''),
                            html.A(className='button button--orange', href='/data/grants.csv', target="_blank", children="Download all grants (CSV)"),
                            ' ',
                            html.A(className='button button--orange', href='/data/grants.json', target="_blank", children="Download all grants (JSON)"),
                            ' ',
                            html.A(className='button button--orange', href="https://grantnav.threesixtygiving.org/search?json_query=%7B%22query%22%3A+%7B%22bool%22%3A+%7B%22must%22%3A+%7B%22query_string%22%3A+%7B%22query%22%3A+%22coronavirus+OR+pandemic+OR+covid+OR+%5C%22covid19%5C%22%22%2C+%22default_field%22%3A+%22%2A%22%7D%7D%2C+%22filter%22%3A+%5B%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%2C+%22must%22%3A+%7B%7D%2C+%22minimum_should_match%22%3A+1%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%7B%22range%22%3A+%7B%22amountAwarded%22%3A+%7B%7D%7D%7D%2C+%22must%22%3A+%7B%7D%2C+%22minimum_should_match%22%3A+1%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%7B%22range%22%3A+%7B%22awardDate%22%3A+%7B%22format%22%3A+%22year%22%2C+%22gte%22%3A+%222020%7C%7C%2Fy%22%2C+%22lte%22%3A+%222020%7C%7C%2Fy%22%7D%7D%7D%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%5D%7D%7D%2C+%22sort%22%3A+%7B%22_score%22%3A+%7B%22order%22%3A+%22desc%22%7D%7D%2C+%22aggs%22%3A+%7B%22fundingOrganization%22%3A+%7B%22terms%22%3A+%7B%22field%22%3A+%22fundingOrganization.id_and_name%22%2C+%22size%22%3A+50%7D%7D%2C+%22recipientOrganization%22%3A+%7B%22terms%22%3A+%7B%22field%22%3A+%22recipientOrganization.id_and_name%22%2C+%22size%22%3A+3%7D%7D%2C+%22recipientRegionName%22%3A+%7B%22terms%22%3A+%7B%22field%22%3A+%22recipientRegionName%22%2C+%22size%22%3A+3%7D%7D%2C+%22recipientDistrictName%22%3A+%7B%22terms%22%3A+%7B%22field%22%3A+%22recipientDistrictName%22%2C+%22size%22%3A+3%7D%7D%2C+%22currency%22%3A+%7B%22terms%22%3A+%7B%22field%22%3A+%22currency%22%2C+%22size%22%3A+3%7D%7D%7D%2C+%22extra_context%22%3A+%7B%22awardYear_facet_size%22%3A+3%2C+%22amountAwardedFixed_facet_size%22%3A+3%7D%7D", target="_blank", children="Search on GrantNav"),
                            html.Div(className="spacer-3"),
                            html.P(
                                html.Small(
                                    html.Em(id="last-updated", children=[
                                        'Last updated ',
                                        "{:%Y-%m-%d %H:%M}".format(data["last_updated"]),
                                    ]),
                                ),
                            ),
                        ]),
                    ]),
                ]),
            ]),
            # subscribe(),
            footer(),
        ]
    )
