import os

import dash_html_components as html
import dash_core_components as dcc

def page_header(data):

    if len(data['filters'].get("funder", [])) == 1:

        funder_id = data['filters']["funder"][0]
        funder_name = None
        for f in data["funders"]:
            if f[0] == funder_id:
                funder_name = f[1]

        file_to_check = os.path.join("commentary", f"{funder_id}.md")
        subheading = ""
        if os.path.exists(file_to_check):
            with open(file_to_check) as a:
                subheading = a.read()

        return [
            html.Hgroup(className="header-group", children=[
                html.H2(className="header-group__title", children=[funder_name]),
                html.H3(className="", children='COVID19 response grants'),
            ]),
            html.P(className="header-group__excerpt", children=dcc.Markdown(subheading, dangerously_allow_html=True)),
        ]

    if len(data['filters'].get("area", [])) == 1:

        area_id = data['filters']["area"][0]
        area_name = None
        for f in data["counties"]:
            if f[0] == area_id:
                area_name = f[1]

        funder_number = "One funder" if len(data["funders"]) == 1 else "{:,.0f} funders".format(len(data["funders"]))


        return [
            html.Hgroup(className="header-group", children=[
                html.H2(className="header-group__title", children=[area_name]),
                html.H3(className="", children='COVID19 response grants from {}'.format(
                    funder_number)),
            ]),
            html.P(className="header-group__excerpt",
                   children=dcc.Markdown('''
Based on grants that have included location information. 
{:,.0f} grants out of a total {:,.0f} include location information.
'''.format(data["has_geo"], data["grant_count"]))),
        ]

    return None
