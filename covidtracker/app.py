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
from .layout import layout
from .components import cards, chart, table, page_header

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
app.layout = layout(data, all_data)

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
     Output(component_id='funder-filter', component_property='options'),
     Output(component_id='page-header', component_property='children')],
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
        ],
        page_header(data),
    )
