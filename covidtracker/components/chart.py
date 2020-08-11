import datetime

import dash_core_components as dcc
import dash_html_components as html
import pandas as pd


def chart(grants, chart_type="amount", show_grantmakers=True, cumulative=True):
    idx = pd.date_range("2020-03-16", datetime.datetime.now())
    if chart_type == "amount":
        byDate = (
            pd.crosstab(
                grants["awardDate"],
                grants["_may_be_regranted"],
                aggfunc="sum",
                values=grants["amountAwarded"],
            )
            .fillna(0)
            .reindex(idx, fill_value=0)
        )
    else:
        byDate = (
            pd.crosstab(
                grants["awardDate"],
                grants["_may_be_regranted"],
                aggfunc="count",
                values=grants["id"],
            )
            .fillna(0)
            .reindex(idx, fill_value=0)
        )

    if cumulative:
        byDate = byDate.cumsum()

    data = []
    if False in byDate.columns:
        data.append(
            {
                "x": [d.to_pydatetime() for d in byDate.index],
                "y": byDate[False].tolist(),
                "type": "scatter",
                "name": "Grants to frontline organisations",
                "fill": "tonexty",
                "mode": "lines",
                "line": {"shape": "hv", "color": "rgb(188,44,38)", "width": 3},
                "stackgroup": "one",
            }
        )
    if True in byDate.columns and show_grantmakers:
        data.append(
            {
                "x": [d.to_pydatetime() for d in byDate.index],
                "y": byDate[True].tolist(),
                "type": "scatter",
                "name": "Grants to other grantmakers",
                "fill": "tonexty",
                "mode": "lines",
                "line": {"shape": "hv", "color": "rgb(77, 172, 182);", "width": 3},
                "stackgroup": "one",
                "visible": show_grantmakers,
            }
        )

    return html.Div(
        className="base-card base-card--red",
        children=[
            html.Div(
                className="base-card__content",
                children=[
                    html.Header(
                        className="base-card__header",
                        children=[
                            html.H3(
                                className="base-card__heading",
                                children="Grants over time",
                            ),
                            dcc.RadioItems(
                                options=[
                                    {
                                        "label": "Cumulative total (£ million)",
                                        "value": "amount",
                                    },
                                    {"label": "Number of grants", "value": "grants"},
                                ],
                                value=chart_type,
                                labelStyle={
                                    "display": "inline-block",
                                    "marginRight": "8px",
                                },
                                inputStyle={"marginRight": "4px"},
                                id="chart-type",
                                className="base-card__subheading",
                            ),
                        ],
                    ),
                    dcc.Graph(
                        id="grants-over-time",
                        figure={
                            "data": data,
                            "layout": {
                                "xaxis": {"showgrid": False},
                                "yaxis": {"showgrid": False},
                                "font": {"family": '"Roboto", sans-serif', "size": 14},
                                "height": 300,
                                "margin": dict(l=40, r=10, t=10, b=40),
                                "legend": {"orientation": "h", "visible": True},
                                "showlegend": True,
                            },
                        },
                        config={"displayModeBar": False, "scrollZoom": False},
                    ),
                ],
            ),
        ],
    )
