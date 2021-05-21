import dash_core_components as dcc
import dash_html_components as html

from ..settings import MAPBOX_STYLE, MAPBOX_TOKEN, SOURCES


def sources(s, without_geo=None):
    if not without_geo:
        without_geo = s.isnull().sum()

    return html.Header(
        className="media-card__byline",
        style={"textAlign": "left"},
        children=[
            html.H4(className="", children="Source for location (number of grants)"),
            html.Ul(
                className="",
                children=[
                    html.Li(
                        className="",
                        children=[SOURCES.get(k, k), ": ", "{:,.0f}".format(v)],
                    )
                    for k, v in s.value_counts().iteritems()
                ]
                + (
                    [
                        html.Li(
                            className="",
                            children=[
                                "No geographical data available: ",
                                "{:,.0f}".format(without_geo),
                            ],
                        )
                    ]
                    if without_geo
                    else []
                ),
            ),
        ],
    )


def geomap(grants):
    geo = (
        grants[["location.latitude", "location.longitude", "location.source"]]
        .join(
            grants.apply(
                lambda g: """£{g[amountAwarded]:,.0f} on {g[awardDate]:%d/%m/%Y}<br>from {g[fundingOrganization.0.name]} to {g[recipientOrganization.0.name]}<br>for {g[title]}""".format(
                    g=dict(**g)
                ),
                axis=1,
            ).rename("tooltip")
        )
        .dropna(subset=["location.latitude", "location.longitude"])
    )

    if len(geo) == 0:
        return None

    center = dict(
        lat=geo["location.latitude"].astype(float).median(),
        lon=geo["location.longitude"].astype(float).median(),
    )

    source_description = sources(
        geo["location.source"], without_geo=(len(grants) - len(geo))
    )

    return html.Div(
        className="media-card media-card--teal",
        children=[
            html.Div(
                className="media-card__content",
                children=[
                    dcc.Graph(
                        id="geo-map",
                        figure={
                            "data": [
                                dict(
                                    type="scattermapbox",
                                    lat=geo["location.latitude"].tolist(),
                                    lon=geo["location.longitude"].tolist(),
                                    text=geo["tooltip"].tolist(),
                                    hoverinfo="text",
                                )
                            ],
                            "layout": {
                                "mapbox": dict(
                                    accesstoken=MAPBOX_TOKEN,
                                    bearing=0,
                                    center=center,
                                    pitch=0,
                                    zoom=5,
                                    style=MAPBOX_STYLE,
                                ),
                                "margin": dict(l=0, r=9, t=0, b=0),
                                "height": 800,
                            },
                        },
                        config={
                            # 'displayModeBar': False,
                            # 'scrollZoom': False,
                        },
                    ),
                    source_description,
                ],
            ),
        ],
    )
