import base64
import io
import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import click
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq
import dash_extensions as dex
import dash_html_components as html
import dash_table
import numpy as np
import pandas as pd
from plotly.express.colors import named_colorscales
import plotly.graph_objs as go
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from dash.exceptions import PreventUpdate
from dash_extensions.snippets import send_file

from mcr.clustering import label_clusters
from mcr.reduction import perform_reducion

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
colorscales = named_colorscales()

cytometry_df = None
rd_df = None
cluster_df = None
columns = []

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True
app.layout = html.Div(
    children=[
        dcc.Tabs(
            id="main-tabs",
            value="tab-upload",
            children=[
                dcc.Tab(
                    label="Upload data",
                    value="tab-upload",
                    children=(
                        [
                            dcc.Upload(
                                id="upload-data",
                                children=html.Div(
                                    ["Drag and Drop or ", html.A("Select Files")]
                                ),
                                style={
                                    "width": "100%",
                                    "height": "60px",
                                    "lineHeight": "60px",
                                    "borderWidth": "1px",
                                    "borderStyle": "dashed",
                                    "borderRadius": "5px",
                                    "textAlign": "center",
                                    "margin": "10px",
                                },
                                # Allow multiple files to be uploaded
                                multiple=False,
                            ),
                            html.Hr(),
                            dcc.Loading(
                                id="upload-data-loading",
                                children=html.Div(id="output-data-upload"),
                                type="default",
                            ),
                        ]
                    ),
                ),
                dcc.Tab(
                    label="Reduce and Cluster",
                    value="tab-reduce",
                    children=(
                        [
                            # hidden signal values to deal with multiple sources
                            # trying to update the possible graph colors
                            dcc.Store(id="color-store-import"),
                            dcc.Store(id="color-store-cluster"),
                            dcc.Store(id="colorscale-store"),
                            html.Div(
                                className="four columns div-for-charts bg-grey",
                                children=[
                                    html.B("Choose dimensional reduction method:"),
                                    dcc.Dropdown(
                                        id="reduce-alg",
                                        options=[
                                            {"label": "UMAP", "value": "umap"},
                                            {"label": "tSNE", "value": "tsne"},
                                            {"label": "PaCMAP", "value": "pacmap"},
                                            {"label": "openTSNE", "value": "opentsne"},
                                            {"label": "optSNE", "value": "optsne"},
                                        ],
                                    ),
                                    html.B("(Optional) Choose columns to ignore:"),
                                    dcc.Dropdown(
                                        id="reduce-columns",
                                        options=[{"label": "None", "value": "None"}],
                                        value=[
                                            "Object Id",
                                            "XMin",
                                            "XMax",
                                            "YMin",
                                            "YMax",
                                            "Cell Area (µm²)",
                                            "Cytoplasm Area (µm²)",
                                            "Membrane Area (µm²)",
                                            "Nucleus Area (µm²)",
                                            "Nucleus Perimeter (µm)",
                                            "Nucleus Roundness",
                                        ],
                                        multi=True,
                                    ),
                                    dbc.Button(
                                        "Perform reduction",
                                        id="reduce-submit",
                                        className="mr-2",
                                    ),
                                    dcc.Loading(
                                        id="reduce-loading",
                                        type="default",
                                        children=html.Div(
                                            id="hidden-div", style={"display": "none"}
                                        ),
                                    ),
                                    html.Span(
                                        id="reduction-complete",
                                        style={"vertical-align": "middle"},
                                    ),
                                    dbc.Button(
                                        "Graph data",
                                        id="reduce-graph",
                                        className="mr-2",
                                    ),
                                    html.Hr(),
                                    dbc.Button(
                                        "Label clusters",
                                        id="cluster-data-btn",
                                        className="mr-1",
                                    ),
                                    html.Div(
                                        "Clustering resolution",
                                        id="hidden-div2",
                                        style={
                                            "width": "100%",
                                            "display": "inline-block",
                                        },
                                    ),
                                    dcc.Slider(
                                        id="cluster-resolution-sldr",
                                        min=0.1,
                                        max=3.0,
                                        value=0.6,
                                        step=0.1,
                                        marks={
                                            0.2: {"label": "0.2"},
                                            0.4: {"label": "0.4"},
                                            0.6: {
                                                "label": "0.6",
                                                "style": {"color": "#f50"},
                                            },
                                            0.8: {"label": "0.8"},
                                            1: {"label": "1.0"},
                                            1.2: {"label": "1.2"},
                                            1.4: {"label": "1.4"},
                                            1.6: {"label": "1.6"},
                                            1.8: {"label": "1.8"},
                                            2: {"label": "2.0"},
                                            2.2: {"label": "2.2"},
                                            2.4: {"label": "2.4"},
                                            2.6: {"label": "2.6"},
                                            2.8: {"label": "2.8"},
                                            3: {"label": "3.0"},
                                        },
                                    ),
                                    html.Div(
                                        "N-nearist neighbors",
                                        id="hidden-div3",
                                        style={
                                            "width": "100%",
                                            "display": "inline-block",
                                        },
                                    ),
                                    dcc.Slider(
                                        id="cluster-n-neighbors-sldr",
                                        min=1,
                                        max=100,
                                        value=30,
                                        step=1,
                                        marks={
                                            10: {"label": "10"},
                                            20: {"label": "20"},
                                            30: {
                                                "label": "30",
                                                "style": {"color": "#f50"},
                                            },
                                            40: {"label": "40"},
                                            50: {"label": "50"},
                                            60: {"label": "60"},
                                            70: {"label": "70"},
                                            80: {"label": "80"},
                                            90: {"label": "90"},
                                            100: {"label": "100"},
                                        },
                                    ),
                                    dcc.Loading(
                                        id="cluster-loading",
                                        type="default",
                                        children=html.Div(
                                            id="hidden-clustering-div",
                                            style={"display": "none"},
                                        ),
                                    ),
                                    html.Hr(),
                                    daq.BooleanSwitch(
                                        id="reduce-append",
                                        on=False,
                                        color="#AA0000",
                                        label="Append to data?",
                                        labelPosition="top",
                                        style={
                                            "height": "50%",
                                            "display": "inline-block",
                                        },
                                    ),
                                    dbc.Button(
                                        "Download data",
                                        id="reduce-data-btn",
                                        className="mr-2",
                                    ),
                                    dex.Download(
                                        id="reduce-download-link",
                                    ),
                                    # dcc.Dropdown(
                                    #     id="
                                    # )
                                ],
                            ),
                            html.Div(
                                className="eight columns div-for-charts bg-grey",
                                children=[
                                    html.Div(
                                        id="hidden-div4",
                                        style={
                                            "height": "100%",
                                            "display": "inline-block",
                                        },
                                    ),
                                    dcc.Dropdown(
                                        id="reduced-data-color",
                                        options=[{"label": "None", "value": "None"}],
                                        value=None,
                                        multi=False,
                                    ),
                                    dcc.Dropdown(
                                        id="plot-colorscale",
                                        options=[
                                            {"value": x, "label": x}
                                            for x in colorscales
                                        ],
                                        value="viridis",
                                    ),
                                    dcc.Graph(
                                        id="reduced-data-plot",
                                        config={"responsive": False},
                                    ),
                                ],
                            ),
                        ]
                    ),
                ),
            ],
        ),
        html.Div(id="main-tabs-content"),
    ]
)


def parse_contents(contents, filename):
    global cytometry_df
    if contents is None:
        raise PreventUpdate

    content_type, content_string = contents.split(",")
    logging.critical(f"{content_type}")
    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV file
            cytometry_df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            logging.critical(f"{cytometry_df.columns[0]}")
        elif "xls" in filename or "xlsx" in filename:
            # Assume that the user uploaded an excel file
            cytometry_df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    if cytometry_df is not None:
        return (
            html.Div(
                [
                    dash_table.DataTable(
                        data=cytometry_df.to_dict("records"),
                        columns=[{"name": i, "id": i} for i in cytometry_df.columns],
                    ),
                ]
            ),
            [{"label": i, "value": i} for i in cytometry_df.columns],
        )
    else:
        return None


@app.callback(
    [
        Output("output-data-upload", "children"),
        Output("reduce-columns", "options"),
        Output("color-store-import", "data"),
    ],
    [
        Input("upload-data", "contents"),
    ],
    State("upload-data", "filename"),
)
def import_data(list_of_contents, list_of_names):
    if list_of_contents is None:
        logging.critical("contents are null")
        return None, None, None
    if list_of_contents is not None:
        logging.critical(f"names: {list_of_names}, type: {type(list_of_names)}")
        children = parse_contents(list_of_contents, list_of_names)
        logging.critical(f"{children[1]}")
        return children[0], children[1], children[1]
    else:
        logging.error("Oh, damn, we fucked up.")
        return None, None, None


@app.callback(
    Output("reduced-data-color", "options"),
    [Input("color-store-import", "data"), Input("color-store-cluster", "data")],
    State("reduced-data-color", "options"),
)
def update_graph_color_options(import_vars=None, cluster_vars=None, extant_vars=None):

    if extant_vars is None:
        extant_vars = list()
    if import_vars is not None:
        extant_vars.extend(x for x in import_vars if x not in extant_vars)
    if cluster_vars is not None:
        extant_vars.extend(x for x in cluster_vars if x not in extant_vars)

    return extant_vars


@app.callback(
    Output("hidden-div", "children"),
    [
        Input("reduce-submit", "n_clicks"),
    ],
    State("reduce-alg", "value"),
    State("reduce-append", "on"),
    State("reduce-columns", "value"),
)
def reduce_data(btn, alg, append, ignore_columns=None):
    global cytometry_df
    global rd_df

    if ignore_columns is None:
        ignore_columns = ()
    if type(ignore_columns) is str:
        ignore_columns = tuple(ignore_columns)

    logging.critical(f"{btn}")
    logging.critical(f"{alg}")
    logging.critical(f"{append}")
    if btn is not None:
        if cytometry_df is not None:
            logging.critical(f"performing {alg}")
            logging.critical(f"ignoring {ignore_columns}")
            df = perform_reducion(
                cytometry_df.iloc[:, ~cytometry_df.columns.isin(ignore_columns)],
                reduction=alg,
            )
            logging.critical(f"finished {alg}")
            if append and rd_df is not None:
                logging.critical("appending data")
                rd_df = pd.concat([rd_df.reset_index(drop=True), df], axis=1)
            else:
                logging.critical("append was False")
                rd_df = df
            logging.critical(f"sanitiy check: {alg} data has {rd_df.shape[1]} columns")
            logging.critical("returning data")
            return html.Div(
                [
                    dash_table.DataTable(
                        data=rd_df.to_dict("records"),
                        columns=[{"name": i, "id": i} for i in rd_df.columns],
                    ),
                ]
            )
        else:
            dbc.Modal(
                [
                    dbc.ModalHeader("No data!"),
                    dbc.ModalBody(
                        f"Please load cytometry data before attempting to performing {alg}."
                    ),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close",
                            id="no-data-to-reduce-modal-close",
                            className="ml-auto",
                        )
                    ),
                ],
                id="no-data-to-reduce-modal",
            )
            return None
    else:
        return None


@app.callback(
    Output("reduce-download-link", "data"),
    [Input("reduce-data-btn", "n_clicks")],
    State("reduce-append", "on"),
)
def func(n_clicks, append_to_input=False):
    temp_path = TemporaryDirectory()
    filename = Path(temp_path.name, "reduced_data.csv")
    logging.critical(f"saving csv at {filename}")

    if append_to_input:
        if rd_df is not None:
            if cluster_df is not None:
                output_df = pd.concat(
                    objs=[
                        cytometry_df.reset_index(drop=True),
                        rd_df.reset_index(drop=True),
                        cluster_df.reset_index(drop=True),
                    ],
                    axis=1,
                )
            else:
                output_df = pd.concat(
                    objs=[
                        cytometry_df.reset_index(drop=True),
                        rd_df.reset_index(drop=True),
                    ],
                    axis=1,
                )
        else:
            if cluster_df is not None:
                output_df = pd.concat(
                    objs=[
                        cytometry_df.reset_index(drop=True),
                        cluster_df.reset_index(drop=True),
                    ],
                    axis=1,
                )
            else:
                output_df = pd.concat(
                    objs=[
                        cytometry_df.reset_index(drop=True),
                    ],
                    axis=1,
                )
    else:
        if rd_df is not None:
            if cluster_df is not None:
                output_df = pd.concat(
                    objs=[
                        rd_df.reset_index(drop=True),
                        cluster_df.reset_index(drop=True),
                    ],
                    axis=1,
                )
            else:
                output_df = pd.concat(
                    objs=[
                        rd_df.reset_index(drop=True),
                    ],
                    axis=1,
                )
        else:
            output_df = None
            dbc.Modal(
                [
                    dbc.ModalHeader("No data!"),
                    dbc.ModalBody("There's no data to return!"),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close",
                            id="no-data-to-return-modal-close",
                            className="ml-auto",
                        )
                    ),
                ],
                id="no-data-to-return-modal",
            )

    if output_df is not None:
        output_df.to_csv(path_or_buf=filename, index=False)
        return send_file(filename.absolute())


@app.callback(
    Output("reduced-data-plot", "figure"),
    [
        Input("reduce-graph", "n_clicks"),
        Input("reduced-data-color", "value"),
        Input("plot-colorscale", "value"),
    ],
)
def update_reduction_graph(btn, color, colorscale):
    if btn is not None:
        if color is None:
            fig = go.Figure(
                data=[
                    go.Scattergl(
                        x=rd_df.iloc[:, 0],
                        y=rd_df.iloc[:, 1],
                        type="scattergl",
                        mode="markers",
                        marker=dict(colorscale="viridis"),
                    )
                ],
                layout=go.Layout(height=750, width=900, autosize=False),
            )
        else:
            logging.critical(f"{color} selected for color")
            if color in cytometry_df.columns:
                logging.critical(f"{color} is in cytometry_df")
                color_data = np.log(cytometry_df[color] + 1)
                logging.critical(f"{color_data}")
            elif color in cluster_df.columns:
                logging.critical(f"{color} is in cluster_df")
                logging.critical("cluster_df.columns")
                color_data = cluster_df[color]
                logging.critical(f"{color_data}")
            else:
                color_data = None

            logging.critical("updating plot")
            logging.critical(f"colorscale is {colorscale}")
            fig = go.Figure(
                data=[
                    go.Scattergl(
                        x=rd_df.iloc[:, 0],
                        y=rd_df.iloc[:, 1],
                        type="scattergl",
                        mode="markers",
                        marker=dict(
                            colorscale=colorscale, color=color_data, showscale=True
                        ),
                    )
                ],
                layout=go.Layout(height=750, width=900, autosize=False),
            )
    else:
        fig = go.Figure(
            data=[
                go.Scattergl(
                    x=None,
                    y=None,
                    type="scattergl",
                )
            ],
            layout=go.Layout(height=750, width=900, autosize=False),
        )

    logging.critical("returning updated graph")
    return fig


@app.callback(
    [
        Output("color-store-cluster", "data"),
        Output("hidden-clustering-div", "children"),
    ],
    [
        Input("cluster-data-btn", "n_clicks"),
        Input("cluster-resolution-sldr", "value"),
        Input("cluster-n-neighbors-sldr", "value"),
    ],
    State("reduce-columns", "value"),
)
def cluster_data(
    btn: int,
    res: float,
    n_neighbors: int,
    ignore_columns: Tuple[str] = (),
) -> Optional[List[Dict[str, str]]]:
    global cluster_df

    logging.critical(f"{btn}")
    logging.critical(f"{res}")
    logging.critical(f"{n_neighbors}")
    if btn is not None:
        if cytometry_df is not None:
            data_use = cytometry_df.loc[:, ~cytometry_df.columns.isin(ignore_columns)]
            logging.critical("performing clustering")
            logging.critical(
                f"data was originally {cytometry_df.shape[0]} by {cytometry_df.shape[1]}"
            )
            logging.critical(
                f"with ignored colums, it is {data_use.shape[0]} by {data_use.shape[1]}"
            )
            clusters = label_clusters(
                data_df=data_use, resolution=res, n_neighbors=n_neighbors
            )
            logging.critical("finished clustering")
            logging.critical("appending data")
            if cluster_df is not None:
                cluster_df[f"res_{res}_neighbors_{n_neighbors}"] = clusters
            else:
                cluster_df = pd.DataFrame(
                    {f"res_{res}_neighbors_{n_neighbors}": clusters}
                )
            return (
                [
                    {
                        "label": f"Cluster res_{res}_neighbors_{n_neighbors}",
                        "value": f"res_{res}_neighbors_{n_neighbors}",
                    }
                ],
                True,
            )

        else:
            dbc.Modal(
                [
                    dbc.ModalHeader("No data!"),
                    dbc.ModalBody(
                        "Please load cytometry data before attempting to perform clustering."
                    ),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close", className="ml-auto")
                    ),
                ],
                id="modal",
            )
            return None, True
    else:
        return None, True


@click.command(
    name="main",
)
@click.option(
    "--debug",
    "-d",
    help="Enable debug mode.",
    default=False,
    show_default=True,
    required=False,
    is_flag=True,
)
def main(debug=False):
    """Run a Dash-based interface for performing
    dimensional reduction and clustering of data.
    """
    if debug:
        app.run_server(debug=True, dev_tools_ui=True, dev_tools_props_check=True)
    else:
        app.run_server(debug=False, dev_tools_ui=False, dev_tools_props_check=False)


if __name__ == "__main__":
    # app.run_server(debug=True)
    main()
