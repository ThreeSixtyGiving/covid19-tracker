import dash_html_components as html


def footer():
    return html.Footer(
        className="footer",
        children=[
            html.Div(
                className="footer__row wrapper",
                children=[
                    html.Div(
                        className="footer__column-2 footer__branding",
                        children=[
                            html.Div(
                                className="footer__logo",
                                children=[
                                    html.A(
                                        href="https://www.threesixtygiving.org",
                                        children=[
                                            html.Img(
                                                src="https://www.threesixtygiving.org/wp-content/themes/360giving2020/assets/images/360-giving-logo-white.svg",
                                                alt="360Giving",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.P(
                                className="footer__tagline",
                                children=["Open data for more effective grantmaking"],
                            ),
                        ],
                    ),
                    html.Div(
                        className="footer__column-1 footer__social",
                        children=[
                            html.A(
                                href="https://github.com/threesixtygiving/",
                                className="github-icon",
                                children=[
                                    html.Img(
                                        src="https://www.threesixtygiving.org/wp-content/themes/360giving2020/assets/images/github-logo.svg",
                                        alt="Check our Github",
                                    ),
                                ],
                            ),
                            html.A(
                                href="https://twitter.com/360Giving/",
                                className="twitter-icon",
                                children=[
                                    html.Img(
                                        src="https://www.threesixtygiving.org/wp-content/themes/360giving2020/assets/images/twitter-logo.svg",
                                        alt="Follow us on Twitter",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="footer__row wrapper",
                children=[
                    html.Div(
                        className="footer__column-1 footer__section medium-up",
                        children=[
                            html.H3(
                                className="footer__heading",
                                children=["For grantmakers"],
                            ),
                            html.Ul(
                                id="menu-for-grantmakers",
                                className="",
                                children=[
                                    html.Li(
                                        id="menu-item-2400",
                                        className="menu-item menu-item-type-post_type menu-item-object-page menu-item-2400",
                                        children=[
                                            html.A(
                                                href="https://www.threesixtygiving.org/support/why-publish-grants-data/",
                                                children=["Why publish?"],
                                            ),
                                        ],
                                    ),
                                    html.Li(
                                        id="menu-item-2401",
                                        className="menu-item menu-item-type-post_type menu-item-object-page menu-item-2401",
                                        children=[
                                            html.A(
                                                href="https://www.threesixtygiving.org/support/standard/",
                                                children=["The Data Standard"],
                                            ),
                                        ],
                                    ),
                                    html.Li(
                                        id="menu-item-2450",
                                        className="menu-item menu-item-type-post_type menu-item-object-page menu-item-2450",
                                        children=[
                                            html.A(
                                                href="https://www.threesixtygiving.org/about/datachampions/",
                                                children=["Data Champions"],
                                            ),
                                        ],
                                    ),
                                    html.Li(
                                        id="menu-item-2403",
                                        className="menu-item menu-item-type-post_type menu-item-object-page menu-item-2403",
                                        children=[
                                            html.A(
                                                href="https://www.threesixtygiving.org/support/",
                                                children=["Support"],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="footer__column-1 footer__section medium-up",
                        children=[
                            html.H3(
                                className="footer__heading",
                                children=["Explore grants data"],
                            ),
                            html.Ul(
                                id="menu-explore-grants-data",
                                className="",
                                children=[
                                    html.Li(
                                        id="menu-item-2405",
                                        className="menu-item menu-item-type-custom menu-item-object-custom menu-item-2405",
                                        children=[
                                            html.A(
                                                href="https://grantnav.threesixtygiving.org/",
                                                children=["GrantNav"],
                                            ),
                                        ],
                                    ),
                                    html.Li(
                                        id="menu-item-2406",
                                        className="menu-item menu-item-type-custom menu-item-object-custom menu-item-2406",
                                        children=[
                                            html.A(
                                                href="http://data.threesixtygiving.org/",
                                                children=["Data Registry"],
                                            ),
                                        ],
                                    ),
                                    html.Li(
                                        id="menu-item-2407",
                                        className="menu-item menu-item-type-custom menu-item-object-custom menu-item-2407",
                                        children=[
                                            html.A(
                                                href="https://insights.threesixtygiving.org/",
                                                children=["360Insights"],
                                            ),
                                        ],
                                    ),
                                    html.Li(
                                        id="menu-item-2408",
                                        className="menu-item menu-item-type-post_type menu-item-object-page menu-item-2408",
                                        children=[
                                            html.A(
                                                href="https://www.threesixtygiving.org/contact/",
                                                children=["Contact"],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="footer__column-2 footer__section",
                        children=[
                            html.H3(
                                className="footer__heading", children=["360Giving"]
                            ),
                            html.Div(
                                className="textwidget",
                                children=[
                                    html.Div(
                                        className="textwidget",
                                        children=[
                                            html.P(
                                                "We help organisations openly publish grants data, and help people use it to improve charitable giving."
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="wrapper footer__small-print",
                children=[
                    html.P(
                        [
                            "© Copyright 2020 360Giving, licensed under a ",
                            html.A(
                                href="https://creativecommons.org/licenses/by/4.0/",
                                target="_blank",
                                children=[
                                    "Creative Commons Attribution 4.0 International License"
                                ],
                            ),
                            ".",
                        ]
                    ),
                ],
            ),
            html.Div(
                className="footer__row wrapper footer__small-print",
                children=[
                    html.Div(
                        className="footer__column-2",
                        children=[
                            html.P(
                                [
                                    "360Giving:" "Company ",
                                    html.A(
                                        href="https://beta.companieshouse.gov.uk/company/09668396",
                                        target="_blank",
                                        children=["09668396"],
                                    ),
                                    "Charity ",
                                    html.A(
                                        href="http://beta.charitycommission.gov.uk/charity-details/?regid=1164883&amp;subid=0",
                                        target="_blank",
                                        children=["1164883"],
                                    ),
                                ]
                            ),
                        ],
                    ),
                    html.Div(
                        className="footer__column-2 footer__policy-links",
                        children=[
                            html.P(
                                [
                                    html.A(
                                        href="https://www.threesixtygiving.org/privacy/",
                                        children=["Privacy Notice"],
                                    ),
                                    " | ",
                                    html.A(
                                        href="https://www.threesixtygiving.org/terms-conditions/",
                                        children=["Terms & Conditions"],
                                    ),
                                    " | ",
                                    html.A(
                                        href="https://www.threesixtygiving.org/cookie-policy/",
                                        children=["Cookie Policy"],
                                    ),
                                    " | ",
                                    html.A(
                                        href="https://www.threesixtygiving.org/take-down-policy/",
                                        children=["Take Down Policy"],
                                    ),
                                    " | ",
                                    html.A(
                                        href="https://www.threesixtygiving.org/about/360giving-code-conduct/",
                                        children=["Code of Conduct"],
                                    ),
                                ]
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
