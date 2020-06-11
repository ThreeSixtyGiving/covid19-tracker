from itertools import accumulate

import dash
import dash_core_components as dcc
import dash_html_components as html

from ._utils import horizontal_bar
from ..settings import THREESIXTY_COLOURS

def top_funders(data):
    funder_counts = data['funder_counts'].most_common(10)
    if len(funder_counts) <= 1:
        return None

    funder_counts = [{
        'name': f[0][1],
        'count': f[1],
    } for f in funder_counts]
    
    return html.Div(
        className="base-card base-card--orange",
        children=[
            html.Div(className="base-card__content", children=[
                html.Header(className="base-card__header", children=[
                    html.H3(className="base-card__heading",
                            children="Funders by grants made"),
                    html.H4(className="base-card__subheading",
                            children="Top {:,.0f}".format(len(funder_counts))),
                ]),
                dcc.Graph(
                    id='top-funders-chart',
                    figure=horizontal_bar(
                        funder_counts,
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
