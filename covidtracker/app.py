import json
import os
from io import StringIO
import csv
import urllib.parse

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask import make_response

from .data import get_data, filter_data
from .components import cards, chart, table

app = dash.Dash(__name__)
server = app.server

with open(os.path.join(os.path.dirname(__file__), 'templates/dash.html'), encoding='utf8') as a:
    app.index_string = a.read()

all_data = get_data()
data = filter_data(all_data)

@server.route('/data/grants.json')
def get_all_grants():
    return {
        "grants": data['grants']
    }

@server.route('/data/grants.csv')
def get_all_grants_csv():

    def trim_date(value):
        if not value:
            return value
        return value[0:10]

    outputStream = StringIO()
    writer = csv.DictWriter(outputStream, fieldnames=[
        "Identifier",                      # id
        "Title",                           # title
        "Description",                     # description
        "Currency",                        # currency
        "Amount Awarded",                  # amountAwarded
        "Award Date",                      # awardDate
        "Planned Dates:Start Date",        # plannedDates.0.endDate
        "Planned Dates:End Date",          # plannedDates.0.startDate
        "Planned Dates:Duration (months)", # plannedDates.0.duration
        "Recipient Org:Identifier",        # recipientOrganization.0.id
        "Recipient Org:Name",              # recipientOrganization.0.name
        "Recipient Org:Charity Number",    # recipientOrganization.0.charityNumber
        "Recipient Org:Company Number",    # recipientOrganization.0.companyNumber
        "Recipient Org:Postal Code",       # recipientOrganization.0.postalCode
        "Funding Org:Identifier",          # fundingOrganization.0.id
        "Funding Org:Name",                # fundingOrganization.0.name
        "Grant Programme:Title",           # grantProgramme.0.title
    ])
    writer.writeheader()
    for g in data["grants"]:
        writer.writerow({
            "Identifier":                       g.get('id'),                      # id
            "Title":                            g.get("title"),                           # title
            "Description":                      g.get("description"),                     # description
            "Currency":                         g.get("currency"),                        # currency
            "Amount Awarded":                   g.get("amountAwarded"),                  # amountAwarded
            "Award Date":                       trim_date(g.get("awardDate")),                      # awardDate
            "Planned Dates:Start Date":         trim_date(g.get("plannedDates", [{}])[0].get("startDate")),        # plannedDates.0.startDate
            "Planned Dates:End Date":           trim_date(g.get("plannedDates", [{}])[0].get("endDate")),          # plannedDates.0.endDate
            "Planned Dates:Duration (months)":  g.get("plannedDates", [{}])[0].get("duration"), # plannedDates.0.duration
            "Recipient Org:Identifier":         g.get("recipientOrganization", [{}])[0].get("id"), # recipientOrganization.0.id
            "Recipient Org:Name":               g.get("recipientOrganization", [{}])[0].get("name"), # recipientOrganization.0.name
            "Recipient Org:Charity Number":     g.get("recipientOrganization", [{}])[0].get("charityNumber"), # recipientOrganization.0.charityNumber
            "Recipient Org:Company Number":     g.get("recipientOrganization", [{}])[0].get("companyNumber"), # recipientOrganization.0.companyNumber
            "Recipient Org:Postal Code":        g.get("recipientOrganization", [{}])[0].get("postalCode"), # recipientOrganization.0.postalCode
            "Funding Org:Identifier":           g.get("fundingOrganization", [{}])[0].get("id"), # fundingOrganization.0.id
            "Funding Org:Name":                 g.get("fundingOrganization", [{}])[0].get("name"), # fundingOrganization.0.name
            "Grant Programme:Title":            g.get("grantProgramme", [{}])[0].get("title"), # grantProgramme.0.title
        })

    output = make_response(outputStream.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=grants.csv"
    output.headers["Content-type"] = "text/csv"
    return output

app.title = 'Coronavirus response grants tracker'
app.layout = html.Div(id="main-div", children=[
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='filters'),
    html.Div(id="data-cards", children=cards(data)),
    html.Div(className="spacer-3"),
    html.Div(className="filter-section", children=[
        html.Div(className="wrapper filter-section__panel", children=[
            html.Div(className="filter-section__buttons filters", children=[
                dcc.Dropdown(
                    options=[
                        {'label': fname, 'value': fid}
                        for fid, fname in sorted(all_data["funders"], key=lambda x: x[1])
                    ],
                    searchable=True,
                    multi=True,
                    id="funder-filter",
                    style={
                        'width': '300px',
                        'fontSize': '14px',
                        'textAlign': 'left',
                        # 'marginTop': '8px',
                        # 'marginBottom': '8px',
                    },
                    placeholder="Filter by funder...",
                    className='f6'
                ),
            ]),
            html.Div(className='filter-section__search', children=[
                dcc.Input(
                    id="search-filter",
                    type="search",
                    placeholder="Search grants...",
                    className="search-field",
                ),
            ]),
        ]),
    ]),
    html.Div(className="spacer-3"),
    html.Div(className="grid grid--two-columns", children=[
        html.Div(id="data-chart", className="grid__all", children=[
            chart(data),
        ]),
    ]),
    html.Div(className="spacer-3"),
    html.Div(className="grid grid--two-columns", children=[
        html.Div(className="grid__1", children=[
            dcc.Markdown('''
                This data is based on UK foundations reporting grants using the
                360Giving Data Standard. It only includes grants awarded in 
                British Pounds that have already been made (rather than amounts 
                committed to grant programmes).
                
                Not all foundations publish their grants as open data, and some
                publishers do not immediately publish their latest data. 
            ''')
        ]),
        html.Div(className="grid__1", children=[
            dcc.Markdown('''
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
            html.A(className='button button--orange', href='/data/grants.csv', target="_blank", children="Download (CSV)"),
            ' ',
            html.A(className='button button--orange', href='/data/grants.json', target="_blank", children="Download (JSON)"),
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
])

@app.callback(
    [Output(component_id='filters', component_property='data'),
     Output(component_id='url', component_property='pathname'),
     Output(component_id='url', component_property='search')],
    [Input(component_id='funder-filter', component_property='value'),
     Input(component_id='search-filter', component_property='value'),
     Input(component_id='doublecount-filter', component_property='value')]
)
def update_output_div(funder_value, search_value, doublecount_value):

    filters = {
        "funder": funder_value,
        "search": search_value,
        "doublecount": doublecount_value,
    }

    base = '/'
    if funder_value:
        base = '/funder/' + "+".join(funder_value)
    query_params = {}
    if search_value:
        query_params['search'] = search_value
    if doublecount_value and 'exclude' in doublecount_value:
        query_params['exclude'] = True
    if query_params:
        return (filters, base, "?" + urllib.parse.urlencode(query_params))
    return (filters, base, "")


@app.callback(
    [Output(component_id='funder-filter', component_property='value'),
     Output(component_id='search-filter', component_property='value'),
     Output(component_id='doublecount-filter', component_property='value')],
    [Input(component_id='url', component_property='href')]
)
def update_output_div(url):
    url = urllib.parse.urlparse(url)
    filters = {}
    if url.path and url.path !="/":
        filters["funder"] = url.path.replace("/funder/", "").split("+")
    if url.query:
        params = urllib.parse.parse_qs(url.query)
        if params.get("search"):
            filters["search"] = params.get("search")
        if params.get("exclude"):
            filters["exclude"] = ['exclude']
    return (
        filters.get("funder", []),
        filters.get("search", ''),
        filters.get("exclude", []),
    )



@app.callback(
    [Output(component_id='data-cards', component_property='children'),
     Output(component_id='data-chart', component_property='children'),
     Output(component_id='data-table', component_property='children'),
     Output(component_id='last-updated', component_property='children'),
     Output(component_id='funder-filter', component_property='options')],
    [Input(component_id='filters', component_property='data'),
     Input(component_id='chart-type', component_property='value')]
)
def update_output_div(filters, chart_type):

    all_data = get_data()
    data = filter_data(all_data, **filters)

    show_grantmakers = data['grants_grantmakers'] > 0

    return (
        cards(data),
        chart(data, chart_type, show_grantmakers=show_grantmakers),
        table(data),
        [
            'Last updated ',
            "{:%Y-%m-%d %H:%M}".format(data["last_updated"]),
        ],
        [
            {'label': fname, 'value': fid}
            for fid, fname in sorted(all_data["funders"], key=lambda x: x[1])
        ]
    )
