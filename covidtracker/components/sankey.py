from dash import dcc, html

from covidtracker.settings import THREESIXTY_COLOURS


def sankey(grants, all_grants, funder_id, funder_name):
    name_for_other_recipients = "Grant recipients"
    nodes = [funder_name, name_for_other_recipients]
    links = []

    # find grants where the funder is a recipient
    funder_is_recipient = (
        all_grants[all_grants["recipientOrganization.0.id"] == funder_id]
        .groupby("fundingOrganization.0.name")["amountAwarded"]
        .sum()
    )
    nodes.extend(funder_is_recipient.index.tolist())
    for f, count in funder_is_recipient.items():
        links.append(
            (
                nodes.index(f),
                nodes.index(funder_name),
                count,
            )
        )

    # count grants from this funder where the recipient is not a funder
    recipient_isnt_funder = all_grants.loc[
        (all_grants["fundingOrganization.0.id"] == funder_id)
        & ~all_grants["_may_be_regranted"],
        :,
    ]["amountAwarded"].sum()
    links.append(
        (
            nodes.index(funder_name),
            nodes.index(name_for_other_recipients),
            recipient_isnt_funder,
        )
    )

    # find grants from this funder where the recipient is a funder
    recipient_is_funder = (
        all_grants[
            (all_grants["fundingOrganization.0.id"] == funder_id)
            & all_grants["_may_be_regranted"]
        ]
        .groupby("recipientOrganization.0.name")["amountAwarded"]
        .sum()
    )
    nodes.extend(recipient_is_funder.index.tolist())
    for f, count in recipient_is_funder.items():
        links.append(
            (
                nodes.index(funder_name),
                nodes.index(f),
                count,
            )
        )
        links.append(
            (
                nodes.index(f),
                nodes.index(name_for_other_recipients),
                count,
            )
        )

    # if we haven't got any links then we don't display the chart
    if len(links) <= 1:
        return None

    # work out the colours for the nodes
    node_colours = []
    link_colours = []
    for n in nodes:
        if n == funder_name:
            node_colours.append(THREESIXTY_COLOURS[0])
        elif n == name_for_other_recipients:
            node_colours.append(THREESIXTY_COLOURS[1])
        else:
            node_colours.append(THREESIXTY_COLOURS[2])

    for link in links:
        if link[0] == nodes.index(funder_name):
            link_colours.append("#F7DBC9")  # light orange
        elif link[0] == nodes.index(name_for_other_recipients):
            link_colours.append("#D3EAED")  # light teal
        else:
            link_colours.append("#FBF0C9")  # light yellow

    return html.Div(
        className="",
        children=[
            html.H3(className="", children="Funding flows"),
            dcc.Markdown(
                """
            This shows any grants this funder has made to other funders,
            and any grants this funder has received.

            Note that the flows shown here do not necessarily reflect
            how funding has been allocated, and may not include other
            grants made by those funders.
        """
            ),
            dcc.Graph(
                id="sankey-chart",
                figure=dict(
                    data=[
                        dict(
                            type="sankey",
                            node=dict(
                                pad=15,
                                thickness=50,
                                line=dict(color="black", width=0),
                                label=nodes,
                                color=node_colours,
                                hovertemplate="%{label}",
                            ),
                            link=dict(
                                source=[x[0] for x in links],
                                target=[x[1] for x in links],
                                value=[x[2] for x in links],
                                color=link_colours,
                                hovertemplate=" %{value} from %{source.label}<br />"
                                + "to %{target.label}",
                            ),
                        )
                    ],
                    layout={
                        "font": {"family": '"Roboto", sans-serif', "size": 14},
                        "margin": dict(l=40, r=24, b=40, t=24, pad=4),
                        "height": 200,
                    },
                ),
                config={"displayModeBar": False, "scrollZoom": False},
            ),
        ],
    )
