from itertools import accumulate

import dash
import dash_core_components as dcc
import dash_html_components as html

def chart(data):
    return html.Div(
        className="base-card base-card--red",
        children=[
            html.Div(className="base-card__content", children=[
                html.Header(className="base-card__header", children=[
                    html.H3(className="base-card__heading", children="Grants over time"),
                    html.H4(className="base-card__subheading", children="Cumulative total (£ million)"),
                ]),
                dcc.Graph(
                    id='grants-over-time',
                    figure={
                        'data': [
                            {
                                'x': list(data["amountByDate"].keys()),
                                'y': list(accumulate([d["amount"] for d in data["amountByDate"].values()])),
                                'type': 'scatter',
                                'name': 'Grant amount',
                                'fill': 'tozeroy',
                                'mode': 'lines',
                                'line': {
                                    'shape': 'vh',
                                    'color': 'rgb(188,44,38)',
                                    'width': 3,
                                }
                            },
                        ],
                        'layout': {
                            'xaxis': {
                                'showgrid': False,
                            },
                            'yaxis': {
                                'showgrid': False,
                            },
                            'font': {
                                'family': '"Roboto", sans-serif',
                                'size': 14,
                            },
                            'height': 300,
                            'margin': dict(l=40, r=10, t=10, b=40),
                        },
                    },
                    config={
                        'displayModeBar': False,
                        'scrollZoom': False,
                    }
                ),
            ]),
        ],
    )