import os

import dash_core_components as dcc
import dash_html_components as html

from ..settings import FUNDER_GROUPS
from .sankey import sankey


def page_header(data):
    grants = data["grants"]

    if len(data["filters"].get("funder", [])) == 1:

        funder_id = data["filters"]["funder"][0]
        if funder_id in FUNDER_GROUPS.keys():
            funder_name = FUNDER_GROUPS[funder_id]["name"]
        else:
            funder_name = grants.loc[
                grants["fundingOrganization.0.id"] == funder_id,
                "fundingOrganization.0.name",
            ].iloc[-1]

        file_to_check = os.path.join("commentary", f"{funder_id}.md")
        subheading = ""
        if os.path.exists(file_to_check):
            with open(file_to_check) as a:
                subheading = a.read()

        # lottery specific output added after subheading
        if funder_id == "lottery":
            subheading += "Lottery distributors have published the following data related to COVID19 response:\n\n"
            for f_id, f_name in FUNDER_GROUPS["lottery"]["funder_ids"].items():
                subheading += " - {}: {:,.0f} grants\n".format(
                    f_name,
                    (data["all_grants"]["fundingOrganization.0.id"] == f_id).sum(),
                )

        return [
            html.Hgroup(
                className="header-group",
                children=[
                    html.H2(className="header-group__title", children=[funder_name]),
                    html.H3(className="", children="COVID19 response grants"),
                ],
            ),
            html.P(
                className="header-group__excerpt",
                children=dcc.Markdown(subheading, dangerously_allow_html=True),
            )
            if subheading
            else None,
            sankey(
                data["grants"],
                data["all_grants"],
                funder_id=funder_id,
                funder_name=funder_name,
            ),
        ]

    if len(data["filters"].get("area", [])) == 1:

        area_id = data["filters"]["area"][0]
        area_name = grants.loc[
            grants["location.utlacd"] == area_id, "location.utlanm"
        ].iloc[-1]

        funder_count = len(grants["fundingOrganization.0.id"].unique())
        funder_number = (
            "One funder"
            if funder_count == 1
            else "{:,.0f} funders".format(funder_count)
        )

        grant_count = len(grants)
        with_geo = grants["location.source"].notnull().sum()

        return [
            html.Hgroup(
                className="header-group",
                children=[
                    html.H2(className="header-group__title", children=[area_name]),
                    html.H3(
                        className="",
                        children="COVID19 response grants from {}".format(
                            funder_number
                        ),
                    ),
                ],
            ),
            html.P(
                className="header-group__excerpt",
                children=dcc.Markdown(
                    """
Based on grants that have included location information. 
{:,.0f} grants out of a total {:,.0f} include location information.
""".format(
                        with_geo, grant_count
                    )
                ),
            ),
        ]

    return None
