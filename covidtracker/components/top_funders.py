from dash import dcc, html

from covidtracker.components._utils import horizontal_bar
from covidtracker.settings import FUNDER_GROUPS, THREESIXTY_COLOURS


def top_funders(grants, filters, limit=10, start=0):
    funder_counts = (
        grants.groupby("fundingOrganization.0.id")
        .agg(
            {
                "title": "size",
                "fundingOrganization.0.name": "last",
            }
        )
        .rename(
            columns={
                "title": "grants",
                "fundingOrganization.0.name": "funder_name",
            }
        )
    )

    missing_funders = 0
    if filters.get("funder"):
        for f in filters["funder"]:
            if f in FUNDER_GROUPS.keys():
                for funder_id, funder_name in FUNDER_GROUPS[f]["funder_ids"].items():
                    if funder_id not in grants["fundingOrganization.0.id"].unique():
                        # funder_counts.loc[funder_id, "grants"] = 0
                        # funder_counts.loc[funder_id, "funder_name"] = funder_name
                        missing_funders += 1

    if len(funder_counts) == 1:
        funder_str = ""
    elif len(funder_counts) <= limit:
        funder_str = "{:,.0f} funders".format(len(funder_counts))
    else:
        funder_str = "Top {:,.0f} of {:,.0f}".format(limit, len(funder_counts))

    funder_counts = [
        {"name": details["funder_name"], "count": details["grants"]}
        for funder_id, details in funder_counts.sort_values("grants", ascending=False)
        .head(limit)
        .iterrows()
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
                                className="base-card__subheading",
                                children=["Number of grants. ", funder_str],
                            ),
                        ],
                    ),
                    dcc.Graph(
                        id="top-funders-chart",
                        figure=horizontal_bar(
                            funder_counts,
                            colour=THREESIXTY_COLOURS[0],
                        ),
                        config={"displayModeBar": False, "scrollZoom": False},
                    ),
                ]
                + (
                    [
                        html.P(
                            "{:,.0f} funders from this group have not published data yet.".format(
                                missing_funders
                            )
                        )
                    ]
                    if missing_funders
                    else []
                ),
            ),
        ],
    )
