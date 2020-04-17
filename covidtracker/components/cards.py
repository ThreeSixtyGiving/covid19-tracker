import dash
import dash_core_components as dcc
import dash_html_components as html

def cards(data):

    if len(data['funders']) > 1:
        div_class="grid grid--four-columns"
    else:
        div_class="grid grid--three-columns"

    return html.Div(
        className=div_class,
        children=[
            html.Div(className="grid__1", children=[
                html.Div(className="base-card base-card--teal", children=[
                    html.Div(className="base-card__content", children=[
                        html.H2(className="base-card__title", children="{:,.0f}".format(len(data["grants"]))),
                        html.P(className="base-card__text", children="Grants"),
                    ]),
                ]),
            ]),
            html.Div(className="grid__1", children=[
                html.Div(className="base-card base-card--orange", children=[
                    html.Div(className="base-card__content", children=[
                        html.H2(className="base-card__title", children="{:,.0f}".format(len(data["recipients"]))),
                        html.P(className="base-card__text", children="Recipients"),
                    ]),
                ]),
            ]),
            html.Div(className="grid__1", children=[
                html.Div(className="base-card base-card--yellow", children=[
                    html.Div(className="base-card__content", children=[
                        html.H2(className="base-card__title", children="{:,.0f}".format(len(data["funders"]))),
                        html.P(className="base-card__text", children="Funders"),
                    ]),
                ]),
            ]) if len(data["funders"]) > 1 else None,
            html.Div(className="grid__1", children=[
                html.Div(className="base-card base-card--red", children=[
                    html.Div(className="base-card__content", children=[
                        html.H2(className="base-card__title", children="£{:,.0f}".format(data["amountAwarded"].get('GBP', 0))),
                        html.P(className="base-card__text", children="Total"),
                    ]),
                ]),
            ]),
        ],
    )