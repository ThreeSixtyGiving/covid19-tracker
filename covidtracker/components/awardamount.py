from itertools import accumulate

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

from ._utils import horizontal_bar
from ..settings import THREESIXTY_COLOURS, AMOUNT_BINS, AMOUNT_BIN_LABELS


def awardamount(grants):
    amount_bins = pd.cut(
        grants["amountAwarded"],
        bins=AMOUNT_BINS,
        labels=AMOUNT_BIN_LABELS,
    )
    amounts = [
        {
            'name': i,
            'count': count
        }
        for i, count in amount_bins.value_counts().sort_index().iteritems()
    ]
    count_unknown = amount_bins.isnull().sum()
    if count_unknown:
        amounts.append({
            "name": "Unknown",
            "count": count_unknown,
        })

    return html.Div(
        className="base-card base-card--orange grid__1",
        children=[
            html.Div(className="base-card__content", children=[
                html.Header(className="base-card__header", children=[
                    html.H3(className="base-card__heading",
                            children="Grant amount"),
                    html.H4(className="base-card__subheading",
                            children='Number of grants (Registered charities only)'),
                ]),
                dcc.Graph(
                    id='amount-chart-chart',
                    figure=horizontal_bar(
                        amounts,
                        colour=THREESIXTY_COLOURS[0],
                    ),
                    config={
                        'displayModeBar': False,
                        'scrollZoom': False,
                    }
                ),
            ]),
        ],
    )
