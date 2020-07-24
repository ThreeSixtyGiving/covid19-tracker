import dash_core_components as dcc
import dash_html_components as html

from ..settings import THREESIXTY_COLOURS
from ._utils import horizontal_bar
from .geomap import sources


def regions(grants):
    area_types = [
        ("location.ladcd", "location.ladnm", "Local Authority District"),
        ("location.utlacd", "location.utlanm", "Local Authority"),
        ("location.rgncd", "location.rgnnm", "Region"),
    ]
    for a in area_types:
        regions = grants[grants[a[0]] != ""].groupby([a[0], a[1]]).size()
        region_type = a[2]
        if len(regions) > 1 and len(regions) < 100:
            break

    if len(regions) <= 1:
        return None

    regions = [{"name": i[1], "count": count} for i, count in regions.iteritems()]
    subtitle = None
    if region_type.startswith("Local Authority"):
        regions = sorted(regions, key=lambda x: -x["count"])
        if len(regions) > 12:
            regions = regions[:12]
            subtitle = "Top {:,.0f} local authorities".format(12)

    return html.Div(
        className="base-card base-card--teal grid__1",
        children=[
            html.Div(
                className="base-card__content",
                children=[
                    html.Header(
                        className="base-card__header",
                        children=[
                            html.H3(
                                className="base-card__heading",
                                children="Grants by {}".format(region_type),
                            ),
                            html.H4(
                                className="base-card__subheading", children=subtitle
                            )
                            if subtitle
                            else None,
                        ],
                    ),
                    dcc.Graph(
                        id="regions-chart-chart",
                        figure=horizontal_bar(regions, colour=THREESIXTY_COLOURS[1],),
                        config={"displayModeBar": False, "scrollZoom": False},
                    ),
                    sources(grants["location.source"]),
                ],
            ),
        ],
    )
