import copy

import plotly.graph_objs as go
from plotly.subplots import make_subplots

LAYOUT = {
    "yaxis": {
        "automargin": True,
        "visible": False,
        "showgrid": False,
        "showline": False,
        "linewidth": 0,
        "rangemode": "tozero",
        "fixedrange": True,
        "tickfont": {
            # 'size': 20
        },
    },
    "xaxis": {
        "automargin": True,
        "showgrid": False,
        "showline": False,
        "rangemode": "tozero",
        "autorange": True,
        "linewidth": 0,
        "tickfont": {
            # 'size': 20
        },
    },
    "margin": go.layout.Margin(l=40, r=24, b=40, t=24, pad=4),
    "clickmode": "event+select",
    "dragmode": False,
    "paper_bgcolor": "rgba(1, 1, 1, 0.0)",
    "plot_bgcolor": "rgba(1, 1, 1, 0.0)",
    "font": {"family": '"Roboto", sans-serif', "size": 14},
}
H_LAYOUT = {
    "xaxis": copy.deepcopy(LAYOUT["yaxis"]),
    "yaxis": copy.deepcopy(LAYOUT["xaxis"]),
    **{k: copy.deepcopy(v) for k, v in LAYOUT.items() if k not in ["xaxis", "yaxis"]},
}


def horizontal_bar(
    categories,
    value="count",
    text=None,
    log_axis=False,
    colour="#237756",
    text_colour="#fff",
    **kwargs,
):
    # categories = {
    #   "name": "category name"
    #   ...various values
    # }

    if not categories:
        return dict(
            data=[],
            layout={},
        )

    hb_plot = make_subplots(
        rows=len(categories),
        cols=1,
        subplot_titles=[x["name"] for x in categories],
        shared_xaxes=True,
        print_grid=False,
        vertical_spacing=(0.45 / len(categories)),
        **kwargs,
    )
    max_value = max([x[value] for x in categories])
    for k, x in enumerate(categories):
        hb_plot.add_trace(
            dict(
                type="bar",
                orientation="h",
                y=[x["name"]],
                x=[x[value]],
                text=[x.get(text, "{:,.0f}".format(x[value]))],
                hoverinfo="text",
                hoverlabel=dict(
                    bgcolor=colour,
                    bordercolor=colour,
                    font=dict(
                        family='"Roboto", sans-serif',
                        color="#fff",
                    ),
                ),
                textposition="auto"
                if not log_axis or not max_value or ((x[value] / max_value) > 0.05)
                else "outside",
                textfont=dict(
                    family='"Roboto", sans-serif',
                    color=text_colour,
                ),
                marker=dict(
                    color=colour,
                ),
            ),
            k + 1,
            1,
        )

    hb_plot["layout"].update(
        showlegend=False,
        **{
            k: copy.deepcopy(v)
            for k, v in LAYOUT.items()
            if k not in ["xaxis", "yaxis"]
        },
    )

    for x in hb_plot["layout"]["annotations"]:
        x["x"] = 0
        x["xanchor"] = "left"
        x["align"] = "left"
        x["font"] = dict(
            family='"Roboto", sans-serif',
            size=14,
        )

    for x in hb_plot["layout"]:
        if x.startswith("yaxis") or x.startswith("xaxis"):
            hb_plot["layout"][x]["visible"] = False

    if log_axis:
        hb_plot["layout"]["xaxis"]["type"] = "log"

    hb_plot["layout"]["margin"]["l"] = 0
    height_calc = 55 * len(categories)
    height_calc = max([height_calc, 350])
    hb_plot["layout"]["height"] = height_calc

    return dict(
        data=hb_plot.to_dict().get("data", []),
        layout=hb_plot.to_dict().get("layout", {}),
    )
