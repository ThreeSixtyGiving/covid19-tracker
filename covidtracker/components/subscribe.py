import dash_core_components as dcc
import dash_html_components as html

def subscribe():
    return html.Div(className="subscribe-section", children=[
            html.Div(className="subscribe-section__wrapper", children=[
                html.Form(className="subscribe-section__form", action="https://threesixtygiving.us10.list-manage.com/subscribe", method="POST", children=[
                    dcc.Input(type="hidden", name="u", value="216b8b926250184f90c7198e8"),
                    dcc.Input(type="hidden", name="id", value="91870dde44"),
                    dcc.Input(type="email", name="EMAIL", id="EMAIL", placeholder="Subscribe to our newsletter"),
                    dcc.Input(type="submit", value="Submit"),
                ]),
            ]),
        ])
