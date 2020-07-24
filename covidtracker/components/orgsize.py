import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

from ..settings import INCOME_BIN_LABELS, INCOME_BINS, THREESIXTY_COLOURS
from ._utils import horizontal_bar


def orgsize(grants):
    orgsize_bins = pd.cut(
        grants["_recipient_income"], bins=INCOME_BINS, labels=INCOME_BIN_LABELS,
    )
    orgsizes = [
        {"name": i, "count": count}
        for i, count in orgsize_bins.value_counts().sort_index().iteritems()
    ]
    count_unknown = orgsize_bins.isnull().sum()
    if count_unknown:
        orgsizes.append({"name": "Unknown / Not a charity", "count": count_unknown})

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
                                children="Income of recipients",
                            ),
                            html.H4(
                                className="base-card__subheading",
                                children="Number of grants (Registered charities only)",
                            ),
                        ],
                    ),
                    dcc.Graph(
                        id="orgsize-chart-chart",
                        figure=horizontal_bar(orgsizes, colour=THREESIXTY_COLOURS[0],),
                        config={"displayModeBar": False, "scrollZoom": False},
                    ),
                ],
            ),
        ],
    )
