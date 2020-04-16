import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table

def table(data):

    table_data = [
        {
            "fundingOrganization": g["fundingOrganization"][0]["name"],
            "recipientOrganization": g["recipientOrganization"][0]["name"],
            "description": g["title"],
            "amountAwarded": g["amountAwarded"],
            "awardDate": g["awardDate"],
        } for g in data["grants"]
    ]
    table_columns = [
        {"name": 'Funder', "id": 'fundingOrganization'},
        {"name": 'Recipient', "id": 'recipientOrganization'},
        {"name": 'Description', "id": 'description'},
        {"name": '£', "id": 'amountAwarded'},
        {"name": 'Date', "id": 'awardDate'},
    ]

    return html.Div([
        html.H3(className='h3', children="Grants"),
        html.Div(className='table table--zebra', children=[
            # dash_table.DataTable(
            #     id='grantsTable',
            #     columns=table_columns,
            #     data=table_data,
            #     style_data={
            #         'whiteSpace': 'normal',
            #         'height': 'auto'
            #     },
            #     page_size= 10,
            # ),
            html.Table(id='grantsTable', children=[
                html.Thead([
                    html.Tr([
                        html.Th(c['name'])
                        for c in table_columns
                    ]),
                ]),
                html.Tbody([
                    table_row(row, data["all_funders"])
                    for row in data["grants"]
                ])
            ]),
        ]),
    ])

def table_row(g, all_funders):

    if g["recipientOrganization"][0]["id"] in all_funders:
        recipientRow = html.Td(
            className="", 
            children=[
                html.Strong(g["recipientOrganization"][0]["name"]),
                html.Br(),
                html.Small('*This organisation is also a funder so this grant may be intended for re-distribution as grants')
            ], 
            **{"data-header": "Recipient"}
        )
    else:
        recipientRow = html.Td(
            className="table__lead-cell", 
            children=g["recipientOrganization"][0]["name"], 
            **{"data-header": "Recipient"}
        )

    return html.Tr([
        html.Td(
            className="table__lead-cell", 
            children=g["fundingOrganization"][0]["name"],
            **{"data-header": "Funder"}
        ),
        recipientRow,
        html.Td(
            className="",
            children=[
                html.Strong(g["title"]),
                html.Br(),
                g["description"],
                html.Br(),
                html.A(
                    href=f"http://grantnav.threesixtygiving.org/grant/{g['id']}",
                    target="_blank",
                    children="View on GrantNav",
                ),
            ], 
            **{"data-header": "Description"}
        ),
        html.Td(
            className="", 
            children="{:,.0f}".format(g["amountAwarded"]), style={"textAlign": "right"}, 
            **{"data-header": "Amount"}
        ),
        html.Td(
            className="", 
            children=g["awardDate"][0:10], 
            **{"data-header": "Date"}
        ),
    ])