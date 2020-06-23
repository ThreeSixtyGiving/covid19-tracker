from itertools import accumulate

import dash
import dash_core_components as dcc
import dash_html_components as html

from ._utils import horizontal_bar
from ..settings import THREESIXTY_COLOURS

def regions(grants):
    regions = grants[grants['location.rgncd'] != ''].groupby([
        'location.rgncd',
        'location.rgnnm',
    ]).size()
    region_type = 'region'
    if len(regions) <= 1:
        regions = grants[grants['location.utlacd'] != ''].groupby([
            'location.utlacd',
            'location.utlanm',
        ]).size()
        region_type = 'Local Authority'

    if len(regions) <= 1:
        return None

    regions = [
        {
            'name': i[1],
            'count': count
        }
        for i, count in regions.iteritems()
    ]
    subtitle = None
    if region_type == 'Local Authority':
        regions = sorted(regions, key=lambda x: -x['count'])
        if len(regions) > 12:
            regions = regions[:12]
            subtitle = 'Top {:,.0f} local authorities'.format(12)
    
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
