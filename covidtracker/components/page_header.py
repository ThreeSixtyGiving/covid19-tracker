import os

import dash_html_components as html
import dash_core_components as dcc

def page_header(data):
    if len(data["funders"]) != 1:
        return None

    funder_id, funder_name = data["funders"][0]

    file_to_check = os.path.join("commentary", f"{funder_id}.md")
    subheading = ""
    if os.path.exists(file_to_check):
        with open(file_to_check) as a:
            subheading = a.read()

    return [
        html.Hgroup(className="header-group", children=[
            html.H2(className="header-group__title", children=[funder_name]),
            # html.H3(className="header-group__subtitle", children=dcc.Markdown(subheading)),
        ]),
        html.P(className="header-group__excerpt", children=dcc.Markdown(subheading)),
    ]