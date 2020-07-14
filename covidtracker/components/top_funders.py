from itertools import accumulate

import dash
import dash_core_components as dcc
import dash_html_components as html

from ._utils import horizontal_bar
from ..settings import THREESIXTY_COLOURS

def top_funders(grants, show_top=10):
    funder_counts = grants['fundingOrganization.0.name'].value_counts()
    if len(funder_counts) <= 1:
        return None

    if len(funder_counts) > show_top:
        funder_str = "Top {:,.0f} of {:,.0f}".format(
            show_top,
            len(funder_counts)
        )
    else:
        funder_str = "Top {:,.0f}".format(
            len(funder_counts)
        )

    funder_counts = [{
        'name': name,
        'count': count,
    } for name, count in funder_counts.head(show_top).iteritems()]
    
    return html.Div(
        className="base-card base-card--orange grid__1",
        children=[
            html.Div(className="base-card__content", children=[
                html.Header(className="base-card__header", children=[
                    html.H3(className="base-card__heading",
                            children="Funders by grants made"),
                    html.H4(className="base-card__subheading",
                            children=funder_str),
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
