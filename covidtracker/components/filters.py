import dash_core_components as dcc
import dash_html_components as html

from ..settings import FUNDER_GROUPS


def dropdown_options(
    grants, id_field="fundingOrganization.0.id", name_field="fundingOrganization.0.name"
):
    groups = (
        grants.groupby(id_field)
        .agg({name_field: "last", "id": "count", "amountAwarded": "sum"})
        .reset_index()
        .sort_values("id", ascending=False)
    )
    return [
        {"label": f"{f[name_field]} ({f['id']:,.0f})", "value": f[id_field]}
        for _, f in groups.iterrows()
    ]


def filters(grants):

    recipients = grants[["_recipient_id", "_recipient_name"]].copy()
    recipients.loc[:, "_recipient_id"] = recipients["_recipient_id"].fillna(
        grants["recipientOrganization.0.id"]
    )
    recipients.loc[:, "_recipient_name"] = recipients["_recipient_name"].fillna(
        grants["recipientOrganization.0.name"]
    )
    recipients.drop_duplicates().sort_values("_recipient_name")

    funder_options = [
        {"label": group["name"], "value": k} for k, group in FUNDER_GROUPS.items()
    ] + dropdown_options(
        grants,
        id_field="fundingOrganization.0.id",
        name_field="fundingOrganization.0.name",
    )

    return [
        html.Div(
            className="grid grid--four-columns",
            children=[
                html.Div(
                    className="grid__1",
                    children=[
                        dcc.Dropdown(
                            options=funder_options,
                            searchable=True,
                            multi=True,
                            id="funder-filter",
                            style={
                                # 'width': '300px',
                                "fontSize": "14px",
                                "textAlign": "left",
                                # 'marginTop': '8px',
                                # 'marginBottom': '8px',
                            },
                            placeholder="Filter by funder...",
                            className="f6",
                        ),
                    ],
                ),
                html.Div(
                    className="grid__1",
                    children=[
                        dcc.Dropdown(
                            options=[
                                {
                                    "label": r["_recipient_name"],
                                    "value": r["_recipient_id"],
                                }
                                for _, r in recipients.iterrows()
                            ],
                            searchable=True,
                            multi=True,
                            id="recipient-filter",
                            style={
                                # 'width': '300px',
                                "fontSize": "14px",
                                "textAlign": "left",
                                # 'marginTop': '8px',
                                # 'marginBottom': '8px',
                            },
                            placeholder="Filter by recipient...",
                            className="f6",
                        ),
                    ],
                ),
                html.Div(
                    className="grid__1",
                    children=[
                        dcc.Dropdown(
                            options=dropdown_options(
                                grants, "location.utlacd", "location.utlanm"
                            ),
                            searchable=True,
                            multi=True,
                            id="area-filter",
                            style={
                                # 'width': '300px',
                                "fontSize": "14px",
                                "textAlign": "left",
                                # 'marginTop': '8px',
                                # 'marginBottom': '8px',
                            },
                            placeholder="Filter by area...",
                            className="f6",
                        ),
                    ],
                ),
                html.Div(
                    className="grid__1",
                    children=[
                        dcc.Input(
                            id="search-filter",
                            type="search",
                            placeholder="Search grants...",
                            className="search-field",
                        ),
                    ],
                ),
            ],
        ),
    ]
