import dash_core_components as dcc
import dash_html_components as html

def filters(all_data):
    return [
        html.Div(className="wrapper filter-section__panel", children=[
            html.Div(className="filter-section__buttons filters", children=[
                dcc.Dropdown(
                    options=[
                        {'label': fname, 'value': fid}
                        for fid, fname in sorted(all_data["funders"], key=lambda x: x[1])
                    ],
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