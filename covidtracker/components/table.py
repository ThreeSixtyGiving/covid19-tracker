import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash_table.Format import Format, Scheme, Sign, Symbol

def table(data):

    table_data = [
        {
            "fundingOrganization": f'**{g["fundingOrganization"][0]["name"]}**',
            "recipientOrganization": recipient_contents_markdown(g, data["all_funders"]),
            "description": f'''
**{g["title"]}**

{g["description"]}

[View on GrantNav](http://grantnav.threesixtygiving.org/grant/{g['id'].replace(" ", "%20")})
            ''',
            "amountAwarded": g["amountAwarded"],
            "awardDate": g["awardDate"][0:10],
        } for g in data["grants"][::-1]
    ]
    table_columns = [
        {"name": 'Funder', "id": 'fundingOrganization', 'presentation': 'markdown'},
        {"name": 'Recipient', "id": 'recipientOrganization', 'presentation': 'markdown'},
        {"name": 'Description', "id": 'description', 'presentation': 'markdown'},
        {
            "name": '£',
            "id": 'amountAwarded', 
            'type': 'numeric',
            'format': Format(
                precision=0,
                scheme=Scheme.fixed,
                symbol=Symbol.yes,
                symbol_prefix='£',
                group=",",
            ),
        },
        {
            "name": 'Date',
            "id": 'awardDate',
            'type': 'datetime',
        },
    ]

    return dash_table.DataTable(
        id='grantsTable',
        columns=table_columns,
        data=table_data,
        editable=False,
        row_deletable=False,
        sort_action='native',
        style_table={
            'fontFamily': "'Roboto', sans-serif",
            'fontSize': '14px',
        },
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'fontFamily': "'Roboto', sans-serif",
            'fontSize': '14px',
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgba(21, 54, 52, 0.04)',
            }
        ],
        style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
            'fontFamily': "'Roboto', sans-serif",
            'fontSize': '14px',
            'padding': '8px 10px',
            'borderLeft': '0px solid black',
            'borderRight': '0px solid black',
        },
        style_header={
            'background-color': 'rgba(21, 54, 52, 0.1)',
            'fontFamily': "'Roboto', sans-serif",
            'fontSize': '14px',
            'fontWeight': '500',
            'textAlign': 'left',
        },
        page_size= 10,
    )
    # return html.Table(id='grantsTable', children=[
    #     html.Thead([
    #         html.Tr([
    #             html.Th(c['name'])
    #             for c in table_columns
    #         ]),
    #     ]),
    #     html.Tbody([
    #         table_row(row, data["all_funders"])
    #         for row in data["grants"][::-1]
    #     ])
    # ])

def recipient_contents(g, all_funders):
    if g["recipientOrganization"][0]["id"] in all_funders:
        return [
            html.Strong(g["recipientOrganization"][0]["name"]),
            html.Br(),
            html.Small('*This organisation is also a funder so this grant may be intended for re-distribution as grants')
        ]
    else:
        return [g["recipientOrganization"][0]["name"]]

def recipient_contents_markdown(g, all_funders):
    if g["recipientOrganization"][0]["id"] in all_funders:
        return '''
**{}**

*This organisation is also a funder so this grant may be intended for re-distribution as grants
        '''.format(g["recipientOrganization"][0]["name"])
    else:
        return f'**{g["recipientOrganization"][0]["name"]}**'

def description_contents(g):
    return [
        html.Strong(g["title"]),
        html.Br(),
        g["description"],
        html.Br(),
        html.A(
            href=f"http://grantnav.threesixtygiving.org/grant/{g['id']}",
            target="_blank",
            children="View on GrantNav",
        ),
    ]


def table_row(g, all_funders):

    if g["recipientOrganization"][0]["id"] in all_funders:
        recipientRow = html.Td(
            className="", 
            children=recipient_contents(g, all_funders), 
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