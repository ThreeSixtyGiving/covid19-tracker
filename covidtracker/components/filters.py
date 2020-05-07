import dash_core_components as dcc
import dash_html_components as html

def dropdown_options(all_funders):
    funders = sorted([f for f in all_funders], key=lambda x: x[1])
    return [
        {'label': f"{fname} ({all_funders[(fid, fname)]:,.0f})", 'value': fid}
        for fid, fname in funders
    ]

def filters(all_data):
    return [
        html.Div(className="wrapper filter-section__panel", children=[
            html.Div(className="filter-section__buttons filters", children=[
                dcc.Dropdown(
                    options=dropdown_options(all_data['funders']),
                    searchable=True,
                    multi=True,
                    id="funder-filter",
                    style={
                        'width': '300px',
                        'fontSize': '14px',
                        'textAlign': 'left',
                        # 'marginTop': '8px',
                        # 'marginBottom': '8px',
                    },
                    placeholder="Filter by funder...",
                    className='f6'
                ),
            ]),
            html.Div(className="filter-section__buttons filters", children=[
                dcc.Dropdown(
                    options=[
                        {'label': areaname, 'value': areacode}
                        for areacode, areaname in sorted(all_data["counties"], key=lambda x: x[1])
                    ],
                    searchable=True,
                    multi=True,
                    id="area-filter",
                    style={
                        'width': '300px',
                        'fontSize': '14px',
                        'textAlign': 'left',
                        # 'marginTop': '8px',
                        # 'marginBottom': '8px',
                    },
                    placeholder="Filter by area...",
                    className='f6'
                ),
            ]),
            html.Div(className='filter-section__search', children=[
                dcc.Input(
                    id="search-filter",
                    type="search",
                    placeholder="Search grants...",
                    className="search-field",
                ),
            ]),
        ]),
    ]
