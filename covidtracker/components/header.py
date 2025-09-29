from dash import html


def header():
    return html.Header(
        className="layout__header",
        children=[
            html.Div(
                className="hero-section",
                children=[
                    html.Div(
                        className="wrapper",
                        children=[
                            html.Div(
                                className="hero hero--red",
                                children=[
                                    html.Div(
                                        className="hero__column hero__logo",
                                        children=[
                                            html.A(
                                                href="https://threesixtygiving.org/",
                                                children=[
                                                    html.Img(
                                                        src="https://www.360giving.org/wp-content/themes/threesixtygiving/dist/images/logo.svg",
                                                        alt="360 Main",
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="hero__column hero__lead",
                                        children=[
                                            html.H2(
                                                className="hero__title",
                                                children=["COVID-19 Grants Tracker"],
                                            ),
                                            html.P(
                                                className="hero__blurb",
                                                children=[
                                                    "Based on data published by UK grantmakers in the ",
                                                    html.A(
                                                        href="http://standard.threesixtygiving.org/",
                                                        target="_blank",
                                                        children=[
                                                            "360Giving Data Standard"
                                                        ],
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
