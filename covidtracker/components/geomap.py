import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html

from ..settings import THREESIXTY_COLOURS, MAPBOX_TOKEN

def geomap(grants):
    lats = []
    lngs = []
    texts = []
    for i, g in grants.iterrows():
        if g['location.latitude'] and g['location.longitude']:
            lats.append(g['location.latitude'])
            lngs.append(g['location.longitude'])
            texts.append("""£{amountAwarded:,.0f} on {awardDate:%d/%m/%Y}<br>from {funder} to {recipient}<br>for {title}""".format(
                amountAwarded=g["amountAwarded"],
                awardDate=g["awardDate"],
                recipient=g["recipientOrganization.0.name"],
                funder=g["fundingOrganization.0.name"],
                title=g.get("title"),
            ))
    
    if not lats:
        return None

    return None
        
    return html.Div(
        className="base-card base-card--teal",
        children=[
            html.Div(className="base-card__content", children=[
                dcc.Graph(
                    id='geo-map',
                    figure={
                        'data': [dict(
                            type='scattermapbox',
                            lat=lats,
                            lon=lngs,
                            text=texts,
                            hoverinfo='text',
                        )],
                        'layout': {
                            'mapbox': dict(
                                accesstoken=MAPBOX_TOKEN,
                                bearing=0,
                                center=dict(
                                    lat=(sum(lats) / len(lats)),
                                    lon=(sum(lngs) / len(lngs)),
                                ),
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
            ]),
        ],
    )
