import dash
import dash_core_components as dcc
import dash_html_components as html

from ..settings import THREESIXTY_COLOURS, MAPBOX_TOKEN

def geomap(data):
    lats = []
    lngs = []
    for g in data['grants']:
        if g.get("_geo"):
            lat = g["_geo"][0].get("latitude")
            lng = g["_geo"][0].get("longitude")
            if lat and lng:
                lats.append(lat)
                lngs.append(lng)
    
    return html.Div(
        className="base-card base-card--teal",
        children=[
            html.Div(className="base-card__content", children=[
                html.Header(className="base-card__header", children=[
                    html.H3(className="base-card__heading",
                            children="Grants by"),
                ]),
                dcc.Graph(
                    id='geo-map',
                    figure={
                        'data': [{
                            'type': 'scattermapbox',
                            'lat': lats,
                            'lon': lngs,
                        }],
                        'layout': {
                            'mapbox': dict(
                                accesstoken=MAPBOX_TOKEN,
                                bearing=0,
                                center=dict(
                                    lat=sum(lats) / len(lats),
                                    lon=-sum(lngs) / len(lngs)
                                ),
                                pitch=0,
                                zoom=6
                            ),
                            'margin': dict(l=0, r=9, t=0, b=0),
                        }
                    },
                    config={
                        'displayModeBar': False,
                        'scrollZoom': False,
                    }
                ),
            ]),
        ],
    )
