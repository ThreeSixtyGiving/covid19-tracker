from itertools import accumulate

import dash
import dash_core_components as dcc
import dash_html_components as html

from ._utils import horizontal_bar
from ..settings import THREESIXTY_COLOURS

def regions(data):
    regions = data['grantsByRegion']
    region_type = 'region'
    if len(regions) <= 1:
        regions = data['grantsByLa']
        region_type = 'Local Authority'

    if len(regions) <= 1:
        return None

    regions = [{
        'name': code[1],
        **values
    } for code, values in sorted(regions.items())]
    subtitle = None
    if region_type == 'Local Authority':
        regions = sorted(regions, key=lambda x: -x['count'])
        if len(regions) > 12:
            regions = regions[:12]
            subtitle = 'Top {:,.0f} regions'.format(12)
    
    return html.Div(
        className="base-card base-card--teal",
        children=[
            html.Div(className="base-card__content", children=[
                html.Header(className="base-card__header", children=[
                    html.H3(className="base-card__heading",
                            children="Grants by {}".format(region_type)),
                ]),
                dcc.Graph(
                    id='regions-chart-chart',
                    figure=horizontal_bar(
                        regions,
                        colour=THREESIXTY_COLOURS[1],
                    ),
                    config={
                        'displayModeBar': False,
                        'scrollZoom': False,
                    }
                ),
            ]),
        ],
    )
