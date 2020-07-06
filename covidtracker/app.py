import json
import os
from io import StringIO
import csv
import urllib.parse
from collections import defaultdict
import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask import make_response

from .data import get_data, filter_data
from .layout import layout
from .components import (cards, chart, table, page_header, 
                         wordcloud, top_funders, regions,
                         geomap, orgsize, orgtype, awardamount, 
                         datasources)

app = dash.Dash(__name__)
server = app.server

with open(os.path.join(os.path.dirname(__file__), 'templates/dash.html'), encoding='utf8') as a:
    app.index_string = a.read()

all_data = get_data()
data = filter_data(all_data)

@server.route('/data/grants.json')
def get_all_grants():
    return {
        "grants": json.loads(data['grants'].to_json(orient='records'))
    }

@server.route('/data/la.<filetype>')
def get_la_breakdown(filetype="json"):

    las = data['grants'].groupby([
        'location.ladcd', 'location.ladnm'
    ]).aggregate({
        "id": "count",
        "amountAwarded": "sum",
        "_recipient_id": "nunique",
        "fundingOrganization.0.id": "nunique",
    }).rename(columns={
        "id": "grant_count",
        "amountAwarded": "grant_amount_gbp",
        "_recipient_id": "recipients",
        "fundingOrganization.0.id": "funders",
    }).join(
        data['grants'][~data["grants"]['_recipient_is_funder']].groupby([
            'location.ladcd', 'location.ladnm'
        ]).aggregate({
            "id": "count",
            "amountAwarded": "sum"
        }).rename(columns={
            "id": "grant_count_excluding_grantmakers",
            "amountAwarded": "grant_amount_gbp_excluding_grantmakers"
        })
    ).reset_index().rename(columns={
        'location.ladcd': 'lacd',
        'location.ladnm': 'lanm',
    })

    if filetype == 'csv':
        columns = [
            'lacd',
            'lanm',
            'funders',
            'recipients',
            'grant_count',
            'grant_amount_gbp',
            'grant_count_excluding_grantmakers',
            'grant_amount_gbp_excluding_grantmakers',
        ]
        outputStream = StringIO()
        las[columns].to_csv(outputStream, index=False)
        output = make_response(outputStream.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=la.csv"
        output.headers["Content-type"] = "text/csv"
        return output

    output = make_response(las.to_json(orient='records'))
    output.headers['Content-type'] = "application/json"
    return output

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
        "Recipient Is Grantmaker",
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
            "Recipient Is Grantmaker":          g.get("_recipient_is_grantmaker", False),
        })

    output = make_response(outputStream.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=grants.csv"
    output.headers["Content-type"] = "text/csv"
    return output

app.title = 'COVID19 Grants Tracker'
app.layout = layout(data, all_data)

@app.callback(
    [Output(component_id='filters', component_property='data'),
     Output(component_id='url', component_property='pathname'),
     Output(component_id='url', component_property='search')],
    [Input(component_id='funder-filter', component_property='value'),
     Input(component_id='search-filter', component_property='value'),
     Input(component_id='doublecount-filter', component_property='value'),
     Input(component_id='area-filter', component_property='value'),
     Input(component_id='recipient-filter', component_property='value')]
)
def update_output_div(funder_value, search_value, doublecount_value, area_value, recipient_value):
    
    filters = {
        "funder": funder_value,
        "search": search_value,
        "doublecount": doublecount_value,
        "area": area_value,
        "recipient": recipient_value,
    }

    base = '/'
    if funder_value:
        base = '/funder/' + "+".join(funder_value)
    query_params = {}
    if search_value:
        query_params['search'] = search_value
    if doublecount_value and 'exclude' in doublecount_value:
        query_params['exclude'] = True
    if area_value:
        query_params['area'] = " ".join(area_value)
    if recipient_value:
        query_params['recipient'] = " ".join(recipient_value)
    if query_params:
        return (filters, base, "?" + urllib.parse.urlencode(query_params))
    return (filters, base, "")


@app.callback(
    [Output(component_id='funder-filter', component_property='value'),
     Output(component_id='search-filter', component_property='value'),
     Output(component_id='doublecount-filter', component_property='value'),
     Output(component_id='area-filter', component_property='value'),
     Output(component_id='recipient-filter', component_property='value')],
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
            filters["search"] = params.get("search")[0]
        if params.get("exclude"):
            filters["exclude"] = ['exclude']
        if params.get("area"):
            filters["area"] = params.get("area")[0].split(" ")
        if params.get("recipient"):
            filters["recipient"] = params.get("recipient")[0].split(" ")
    return (
        filters.get("funder", []),
        filters.get("search", ''),
        filters.get("exclude", []),
        filters.get("area", []),
        filters.get("recipient", []),
    )



@app.callback(
    [Output(component_id='data-cards', component_property='children'),
     Output(component_id='data-chart', component_property='children'),
     Output(component_id='word-cloud', component_property='children'),
     Output(component_id='data-table', component_property='children'),
     Output(component_id='last-updated', component_property='children'),
     Output(component_id='page-header', component_property='children'),
     Output(component_id='top-funders', component_property='children'),
     Output(component_id='regions-chart', component_property='children'),
     Output(component_id='geomap-container', component_property='children'),
     Output(component_id='organisation-type', component_property='children'),
     Output(component_id='organisation-size', component_property='children'),
     Output(component_id='award-amount', component_property='children'),
     Output(component_id='data-sources', component_property='children')],
    [Input(component_id='filters', component_property='data'),
     Input(component_id='chart-type', component_property='value')]
)
def update_output_div(filters, chart_type):

    all_data = get_data()
    data = filter_data(all_data, **filters)

    show_grantmakers = data['grants']['_recipient_is_funder'].sum() > 0

    return (
        cards(data['grants']),
        chart(data['grants'], chart_type, show_grantmakers=show_grantmakers),
        wordcloud(data['words']),
        table(data['grants']),
        [
            'Last updated ',
            "{:%Y-%m-%d %H:%M}".format(data["last_updated"]),
        ],
        page_header(data),
        top_funders(data['grants']),
        regions(data['grants']),
        geomap(data['grants']),
        orgtype(data['grants']),
        orgsize(data['grants']),
        awardamount(data['grants']),
        datasources(data['grants']),
    )
