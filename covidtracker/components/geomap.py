import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html

from ..settings import THREESIXTY_COLOURS, MAPBOX_TOKEN

def geomap(data):
    lats = []
    lngs = []
    texts = []
    for g in data['grants']:
        if g.get("_geo"):
            lat = g["_geo"][0].get("latitude")
            lng = g["_geo"][0].get("longitude")
            if lat and lng:
                lats.append(lat)
                lngs.append(lng)
                texts.append("""£{amountAwarded:,.0f} on {awardDate:%d/%m/%Y}<br>from {funder} to {recipient}<br>for {title}""".format(
                    amountAwarded=g.get("amountAwarded"),
                    awardDate=datetime.datetime.fromisoformat(g.get("awardDate")[0:10]),
                    recipient=g["recipientOrganization"][0].get("name"),
                    funder=g["fundingOrganization"][0].get("name"),
                    title=g.get("title"),
                ))
    
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
