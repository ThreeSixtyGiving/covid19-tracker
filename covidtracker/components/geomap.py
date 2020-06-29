import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html

from ..settings import THREESIXTY_COLOURS, MAPBOX_TOKEN

def geomap(grants):
    geo = grants[['location.latitude', 'location.longitude', 'location.source']].join(
        grants.apply(lambda g: """£{g[amountAwarded]:,.0f} on {g[awardDate]:%d/%m/%Y}<br>from {g[recipientOrganization.0.name]} to {g[fundingOrganization.0.name]}<br>for {g[title]}""".format(g=dict(**g)), axis=1).rename("tooltip")
    ).dropna(subset=['location.latitude', 'location.longitude'])
    
    if len(geo) == 0:
        return None

    center = dict(
        lat=geo['location.latitude'].astype(float).median(),
        lon=geo['location.longitude'].astype(float).median(),
    )

    sources = {
        'recipientOrganizationPostcode': 'Postcode of recipient organisation',
        'recipientOrganizationLocation': 'Location of recipient organisation',
        'beneficiaryLocation': 'Beneficiary location',
    }
    without_geo = len(grants) - len(geo) 

    source_description = html.Ul(className='insights-card__list', children=[
        html.Li(className='insights-card__item', children=[
            sources.get(k, k),
            ': ',
            '{:,.0f}'.format(v)
        ])
        for k, v in geo['location.source'].value_counts().iteritems()
    ] + ([
        html.Li(className='insights-card__item', children=[
            'No geographical data available: ',
            '{:,.0f}'.format(without_geo)
        ])
    ] if without_geo else []))

    return html.Div(
        className="base-card base-card--teal",
        children=[
            html.Div(className="base-card__content", children=[
                dcc.Graph(
                    id='geo-map',
                    figure={
                        'data': [dict(
                            type='scattermapbox',
                            lat=geo['location.latitude'].tolist(),
                            lon=geo['location.longitude'].tolist(),
                            text=geo['tooltip'].tolist(),
                            hoverinfo='text',
                        )],
                        'layout': {
                            'mapbox': dict(
                                accesstoken=MAPBOX_TOKEN,
                                bearing=0,
                                center=center,
                                pitch=0,
                                zoom=5,
                            ),
                            'margin': dict(l=0, r=9, t=0, b=0),
                            'height': 800,
                        }
                    },
                    config={
                        # 'displayModeBar': False,
                        # 'scrollZoom': False,
                    }
                ),
                html.Header(className="base-card__header", children=[
                    html.H4(className='base-card__heading',
                            children='Source of location information'),
                    source_description,
                ]),
            ]),
        ],
    )
