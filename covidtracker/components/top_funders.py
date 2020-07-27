import dash_core_components as dcc
import dash_html_components as html

from ..settings import THREESIXTY_COLOURS, FUNDER_GROUPS
from ._utils import horizontal_bar


def top_funders(grants, filters, show_top=10):
    funder_counts = grants["fundingOrganization.0.name"].value_counts()

    if filters.get("funder"):
        for f in filters["funder"]:
            if f in FUNDER_GROUPS.keys():
                for funder_id, funder_name in FUNDER_GROUPS[f]["funder_ids"].items():
                    if funder_id not in grants["fundingOrganization.0.id"].unique():
                        funder_counts.loc[funder_name] = 0

    if len(funder_counts) > show_top:
        funder_str = "Top {:,.0f} of {:,.0f}".format(show_top, len(funder_counts))
    else:
        funder_str = "Top {:,.0f}".format(len(funder_counts))

    funder_counts = [
        {"name": name, "count": count}
        for name, count in funder_counts.head(show_top).iteritems()
    ]

    return html.Div(
        className="base-card base-card--orange grid__1",
        children=[
            html.Div(
                className="base-card__content",
                children=[
                    html.Header(
                        className="base-card__header",
                        children=[
                            html.H3(
                                className="base-card__heading",
                                children="Grants made by funder",
                            ),
                            html.H4(
                                className="base-card__subheading", children=funder_str
                            ),
                        ],
                    ),
                    dcc.Graph(
                        id="top-funders-chart",
                        figure=horizontal_bar(
                            funder_counts, colour=THREESIXTY_COLOURS[0],
                        ),
                        config={"displayModeBar": False, "scrollZoom": False},
                    ),
                ],
            ),
        ],
    )
