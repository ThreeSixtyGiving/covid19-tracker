from dash import html


def cards(grants):
    grant_count = len(grants)
    funder_count = len(grants["fundingOrganization.0.id"].unique())
    recipient_count = len(grants["recipientOrganization.0.id"].unique())
    amount_awarded = grants.loc[grants["currency"] == "GBP", "amountAwarded"].sum()

    if funder_count > 1:
        div_class = "grid grid--four-columns"
    else:
        div_class = "grid grid--three-columns"

    return html.Div(
        className=div_class,
        children=[
            html.Div(
                className="grid__1",
                children=[
                    html.Div(
                        className="base-card base-card--teal",
                        children=[
                            html.Div(
                                className="base-card__content",
                                children=[
                                    html.H2(
                                        className="base-card__title",
                                        children="{:,.0f}".format(grant_count),
                                    ),
                                    html.P(
                                        className="base-card__text", children="Grants"
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="grid__1",
                children=[
                    html.Div(
                        className="base-card base-card--orange",
                        children=[
                            html.Div(
                                className="base-card__content",
                                children=[
                                    html.H2(
                                        className="base-card__title",
                                        children="{:,.0f}".format(recipient_count),
                                    ),
                                    html.P(
                                        className="base-card__text",
                                        children="Recipients",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="grid__1",
                children=[
                    html.Div(
                        className="base-card base-card--yellow",
                        children=[
                            html.Div(
                                className="base-card__content",
                                children=[
                                    html.H2(
                                        className="base-card__title",
                                        children="{:,.0f}".format(funder_count),
                                    ),
                                    html.P(
                                        className="base-card__text", children="Funders"
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            )
            if funder_count > 1
            else None,
            html.Div(
                className="grid__1",
                children=[
                    html.Div(
                        className="base-card base-card--red",
                        children=[
                            html.Div(
                                className="base-card__content",
                                children=[
                                    html.H2(
                                        className="base-card__title",
                                        children="£{:,.0f}".format(amount_awarded),
                                    ),
                                    html.P(
                                        className="base-card__text", children="Total"
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
