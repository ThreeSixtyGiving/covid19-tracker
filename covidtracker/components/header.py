import dash_html_components as html


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
                                                        src="https://www.threesixtygiving.org/wp-content/themes/360giving2020/assets/images/360-logos/360giving-main.svg",
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
