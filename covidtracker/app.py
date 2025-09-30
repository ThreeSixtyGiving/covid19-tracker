import json
import os
import urllib.parse
from io import StringIO

import dash
from dash.dependencies import Input, Output
from flask import make_response, request
from flask_caching import Cache
from prometheus_client import Gauge
from prometheus_client.exposition import generate_latest

from covidtracker.commands.fetch_data import fetch_data
from covidtracker.components import (
    awardamount,
    cards,
    chart,
    datasources,
    geomap,
    orgsize,
    orgtype,
    page_header,
    regions,
    table,
    top_funders,
    wordcloud,
)
from covidtracker.data import filter_data, get_data
from covidtracker.layout import layout
from covidtracker.settings import (
    CACHE_SETTINGS,
    CACHE_TIMEOUT,
    GRANTS_DATA_FILE,
    PROMETHEUS_AUTH_PASSWORD,
    PROMETHEUS_AUTH_USERNAME,
)

external_stylesheets = []
meta_tags = [
    {"charset": "utf-8"},
    {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
    {"http-equiv": "X-UA-Compatible", "content": "ie=edge"},
]

app = dash.Dash(
    __name__, external_stylesheets=external_stylesheets, meta_tags=meta_tags
)
server = app.server
if os.environ.get("FLASK_ENV", "production") == "development":
    CACHE_SETTINGS["CACHE_TYPE"] = "null"
cache = Cache(server, config=CACHE_SETTINGS)

with open(
    os.path.join(os.path.dirname(__file__), "templates/dash.html"), encoding="utf8"
) as a:
    app.index_string = a.read()

server.cli.add_command(fetch_data)


@server.cli.command("clear-cache")
def clear_cache():
    cache.clear()


@server.route("/data/grants.json")
def get_all_grants():
    with open(GRANTS_DATA_FILE, "r") as a:
        return json.load(a)


@server.route("/data/la.<filetype>")
def get_la_breakdown(filetype="json"):
    all_data = get_data()
    data = filter_data(all_data)

    las = (
        data["grants"]
        .groupby(["location.ladcd", "location.ladnm"])
        .aggregate(
            {
                "id": "count",
                "amountAwarded": "sum",
                "_recipient_id": "nunique",
                "fundingOrganization.0.id": "nunique",
            }
        )
        .rename(
            columns={
                "id": "grant_count",
                "amountAwarded": "grant_amount_gbp",
                "_recipient_id": "recipients",
                "fundingOrganization.0.id": "funders",
            }
        )
        .join(
            data["grants"][~data["grants"]["_may_be_regranted"]]
            .groupby(["location.ladcd", "location.ladnm"])
            .aggregate({"id": "count", "amountAwarded": "sum"})
            .rename(
                columns={
                    "id": "grant_count_excluding_grantmakers",
                    "amountAwarded": "grant_amount_gbp_excluding_grantmakers",
                }
            )
        )
        .reset_index()
        .rename(columns={"location.ladcd": "lacd", "location.ladnm": "lanm"})
    )

    if filetype == "csv":
        columns = [
            "lacd",
            "lanm",
            "funders",
            "recipients",
            "grant_count",
            "grant_amount_gbp",
            "grant_count_excluding_grantmakers",
            "grant_amount_gbp_excluding_grantmakers",
        ]
        outputStream = StringIO()
        las[columns].to_csv(outputStream, index=False)
        output = make_response(outputStream.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=la.csv"
        output.headers["Content-type"] = "text/csv"
        return output

    output = make_response(las.to_json(orient="records"))
    output.headers["Content-type"] = "application/json"
    return output


@server.route("/data/grants.csv")
def get_all_grants_csv():
    all_data = get_data()
    data = filter_data(all_data)

    outputStream = StringIO()
    column_renames = {
        "id": "Identifier",
        "title": "Title",
        "description": "Description",
        "currency": "Currency",
        "amountAwarded": "Amount Awarded",
        "awardDate": "Award Date",
        "recipientOrganization.0.id": "Recipient Org:Identifier",
        "recipientOrganization.0.name": "Recipient Org:Name",
        "fundingOrganization.0.id": "Funding Org:Identifier",
        "fundingOrganization.0.name": "Funding Org:Name",
        "grantProgramme.0.title": "Grant Programme:Title",
        "location.ladcd": "Location:ladcd",
        "location.ladnm": "Location:ladnm",
        "location.utlacd": "Location:utlacd",
        "location.utlanm": "Location:utlanm",
        "location.rgncd": "Location:rgncd",
        "location.rgnnm": "Location:rgnnm",
        "location.ctrycd": "Location:ctrycd",
        "location.ctrynm": "Location:ctrynm",
        "location.latitude": "Location:latitude",
        "location.longitude": "Location:longitude",
        "location.source": "Location:source",
        "publisher.prefix": "Publisher:Prefix",
        "publisher.name": "Publisher:Name",
        "license": "Licence",
        "license_name": "Licence Name",
    }
    data["grants"].rename(columns=column_renames).to_csv(outputStream, index=False)
    output = make_response(outputStream.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=grants.csv"
    output.headers["Content-type"] = "text/csv"
    return output


PROMETHEUS_GRANTS_COUNT_GAUGE = Gauge(
    "covid19_tracker_grants_count", "Count of grants in the Covid 19 Tracker"
)

PROMETHEUS_RECIPIENTS_COUNT_GAUGE = Gauge(
    "covid19_tracker_recipients_count", "Count of recipients in the Covid 19 Tracker"
)

PROMETHEUS_FUNDERS_COUNT_GAUGE = Gauge(
    "covid19_tracker_funders_count", "Count of funders in the Covid 19 Tracker"
)

PROMETHEUS_AMOUNT_AWARDED_GBP_GAUGE = Gauge(
    "covid19_tracker_amount_awarded_gbp",
    "Amount Awarded in the Covid 19 Tracker in GBP",
)


@server.route("/prometheus/metrics")
def prometheus_metrics():
    # check auth
    if (
        not request.authorization
        or request.authorization.username != PROMETHEUS_AUTH_USERNAME
        or request.authorization.password != PROMETHEUS_AUTH_PASSWORD
    ):
        return (
            "Unauthorized",
            401,
            {"WWW-Authenticate": 'Basic realm="Login Required"'},
        )

    # update metrics
    data = get_data()
    PROMETHEUS_GRANTS_COUNT_GAUGE.set(len(data["grants"]))
    PROMETHEUS_RECIPIENTS_COUNT_GAUGE.set(
        len(data["grants"]["recipientOrganization.0.id"].unique())
    )
    PROMETHEUS_FUNDERS_COUNT_GAUGE.set(
        len(data["grants"]["fundingOrganization.0.id"].unique())
    )
    PROMETHEUS_AMOUNT_AWARDED_GBP_GAUGE.set(
        data["grants"].loc[data["grants"]["currency"] == "GBP", "amountAwarded"].sum()
    )
    # Send output
    output = make_response(generate_latest())
    output.headers["Content-type"] = "text/plain"
    return output


app.title = "COVID-19 Grants Tracker"
app.layout = layout()


@app.callback(
    [
        Output(component_id="filters", component_property="data"),
        Output(component_id="url", component_property="pathname"),
        Output(component_id="url", component_property="search"),
    ],
    [
        Input(component_id="funder-filter", component_property="value"),
        Input(component_id="search-filter", component_property="value"),
        Input(component_id="doublecount-filter", component_property="value"),
        Input(component_id="area-filter", component_property="value"),
        Input(component_id="recipient-filter", component_property="value"),
    ],
)
def update_url_from_filters(
    funder_value, search_value, doublecount_value, area_value, recipient_value
):
    filters = {
        "funder": funder_value,
        "search": search_value,
        "doublecount": doublecount_value,
        "area": area_value,
        "recipient": recipient_value,
    }

    base = "/"
    if funder_value:
        base = "/funder/" + "+".join(funder_value)
    query_params = {}
    if search_value:
        query_params["search"] = search_value
    if doublecount_value and "exclude" in doublecount_value:
        query_params["exclude"] = True
    if area_value:
        query_params["area"] = " ".join(area_value)
    if recipient_value:
        query_params["recipient"] = " ".join(recipient_value)
    if query_params:
        return (filters, base, "?" + urllib.parse.urlencode(query_params))
    return (filters, base, "")


@app.callback(
    [
        Output(component_id="funder-filter", component_property="value"),
        Output(component_id="search-filter", component_property="value"),
        Output(component_id="doublecount-filter", component_property="value"),
        Output(component_id="area-filter", component_property="value"),
        Output(component_id="recipient-filter", component_property="value"),
    ],
    [Input(component_id="url", component_property="href")],
)
def update_filters_from_url(url):
    url = urllib.parse.urlparse(url)
    filters = {}
    if url.path and url.path != "/":
        filters["funder"] = url.path.replace("/funder/", "").split("+")
    if url.query:
        params = urllib.parse.parse_qs(url.query)
        if params.get("search"):
            filters["search"] = params.get("search")[0]
        if params.get("exclude"):
            filters["exclude"] = ["exclude"]
        if params.get("area"):
            filters["area"] = params.get("area")[0].split(" ")
        if params.get("recipient"):
            filters["recipient"] = params.get("recipient")[0].split(" ")
    return (
        filters.get("funder", []),
        filters.get("search", ""),
        filters.get("exclude", []),
        filters.get("area", []),
        filters.get("recipient", []),
    )


@app.callback(
    [
        Output(component_id="data-cards", component_property="children"),
        Output(component_id="data-chart", component_property="children"),
        Output(component_id="word-cloud", component_property="children"),
        Output(component_id="data-table", component_property="children"),
        Output(component_id="last-updated", component_property="children"),
        Output(component_id="page-header", component_property="children"),
        Output(component_id="top-funders", component_property="children"),
        Output(component_id="regions-chart", component_property="children"),
        Output(component_id="geomap-container", component_property="children"),
        Output(component_id="organisation-type", component_property="children"),
        Output(component_id="organisation-size", component_property="children"),
        Output(component_id="award-amount", component_property="children"),
        Output(component_id="data-sources", component_property="children"),
    ],
    [
        Input(component_id="filters", component_property="data"),
        Input(component_id="chart-type", component_property="value"),
        Input(component_id="tabs", component_property="value"),
    ],
)
@cache.memoize(timeout=CACHE_TIMEOUT)
def update_output_div(filters, chart_type, tab):
    all_data = get_data()
    data = filter_data(all_data, **filters)

    show_grantmakers = data["grants"]["_may_be_regranted"].sum() > 0

    return (
        cards(data["grants"]),
        chart(data["grants"], chart_type, show_grantmakers=show_grantmakers),
        wordcloud(data["words"]) if tab == "dashboard" else None,
        table(data["grants"]) if tab == "data" else None,
        ["Last updated ", "{:%Y-%m-%d %H:%M}".format(data["last_updated"])],
        page_header(data),
        top_funders(data["grants"], data["filters"]) if tab == "dashboard" else None,
        regions(data["grants"]) if tab == "dashboard" else None,
        geomap(data["grants"]) if tab == "map" else None,
        orgtype(data["grants"]) if tab == "dashboard" else None,
        orgsize(data["grants"]) if tab == "dashboard" else None,
        awardamount(data["grants"]) if tab == "dashboard" else None,
        datasources(data["grants"]) if tab == "data" else None,
    )


@app.callback(
    Output("recipient-filter", "options"),
    Input("recipient-filter", "search_value"),
    dash.State("recipient-filter", "value"),
)
def update_multi_options(search_value, value):
    if not search_value:
        raise dash.exceptions.PreventUpdate

    all_data = get_data()

    recipients = (
        all_data["grants"]
        .loc[
            all_data["grants"]["_recipient_name"].str.contains(
                search_value, case=False, na=False
            )
            | all_data["grants"]["_recipient_id"].isin(value or []),
            ["_recipient_id", "_recipient_name"],
        ]
        .copy()
    )
    recipients.loc[:, "_recipient_id"] = recipients["_recipient_id"].fillna(
        all_data["grants"]["recipientOrganization.0.id"]
    )
    recipients.loc[:, "_recipient_name"] = recipients["_recipient_name"].fillna(
        all_data["grants"]["recipientOrganization.0.name"]
    )
    recipients.drop_duplicates().sort_values("_recipient_name")
    # Make sure that the set values are in the option list, else they will disappear
    # from the shown select list, but still part of the `value`.
    return [
        {
            "label": r["_recipient_name"],
            "value": r["_recipient_id"],
        }
        for _, r in recipients.iterrows()
    ]
