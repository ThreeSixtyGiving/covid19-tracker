import dash_html_components as html


def datasources(grants):
    publishers = grants.groupby(
        ["publisher.prefix", "publisher.name", "license_name", "license"]
    ).size()

    return html.Ul(
        [
            html.Li(
                [
                    p[1],
                    " - {:,.0f} grants".format(grant_count),
                    " (",
                    html.A(p[2], href=p[3], target="_blank"),
                    " - ",
                    html.A(
                        "GrantNav",
                        href="http://grantnav.threesixtygiving.org/publisher/{}".format(
                            p[0]
                        ),
                        target="_blank",
                    ),
                    ")",
                ]
            )
            for p, grant_count in publishers.items()
        ]
    )
