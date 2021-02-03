import base64
import io
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq
import dash_extensions as dex
import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from dash.exceptions import PreventUpdate
from dash_extensions.snippets import send_file

from mcr.reduction import perform_reducion

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
cytometry_df = None
rd_df = None
columns = []

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True
app.layout = html.Div(
    children=[
        html.H1("MCR"),
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
                            html.Div(id="output-data-upload"),
                        ]
                    ),
                ),
                dcc.Tab(
                    label="Reduce",
                    value="tab-reduce",
                    children=(
                        [
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
                                        ],
                                    ),
                                    html.B("(Optional) Choose columns to ignore:"),
                                    dcc.Dropdown(
                                        id="reduce-columns",
                                        options=[{"label": "None", "value": "None"}],
                                        value="",
                                        multi=True,
                                    ),
                                    daq.BooleanSwitch(
                                        id="reduce-append",
                                        on=False,
                                        color="#AA0000",
                                        label="Append to data?",
                                        labelPosition="right",
                                    ),
                                    dbc.Button(
                                        "Submit", id="reduce-submit", className="mr-2"
                                    ),
                                    html.Span(
                                        id="reduction-complete",
                                        style={"vertical-align": "middle"},
                                    ),
                                    dbc.Button(
                                        "Download_data",
                                        id="reduce-data-btn",
                                        className="mr-2",
                                    ),
                                    dex.Download(
                                        id="reduce-download-link",
                                    ),
                                    html.Div(
                                        id="hidden-div", style={"display": "none"}
                                    ),
                                ],
                            ),
                            html.Div(
                                className="four columns div-for-charts bg-grey",
                                children=[
                                    html.Div(id="reduced-data"),
                                ],
                            ),
                        ]
                    ),
                ),
                dcc.Tab(
                    label="Cluster",
                    value="tab-cluster",
                ),
                dcc.Tab(
                    label="Plot",
                    value="tab-plot",
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
    [Output("output-data-upload", "children"), Output("reduce-columns", "options")],
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
)
def update_output(list_of_contents, list_of_names):
    if list_of_contents is None:
        logging.critical("contents are null")
    if list_of_contents is not None:
        logging.critical(f"names: {list_of_names}, type: {type(list_of_names)}")
        children = parse_contents(list_of_contents, list_of_names)
        return children
    else:
        logging.error("Oh, damn, we fucked up.")


@app.callback(
    Output("reduced-data", "children"),
    [
        Input("reduce-submit", "n_clicks"),
        Input("reduce-alg", "value"),
        Input("reduce-append", "on"),
    ],
)
def reduce_data(btn, alg, append):
    global cytometry_df
    global rd_df

    logging.critical(f"{btn}")
    logging.critical(f"{alg}")
    logging.critical(f"{append}")

    if btn is not None:
        if cytometry_df is not None:
            logging.critical(f"performing {alg}")
            df = perform_reducion(cytometry_df, reduction=alg)
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
                        dbc.Button("Close", id="close", className="ml-auto")
                    ),
                ],
                id="modal",
            )
            return None
    else:
        return None


@app.callback(
    Output("reduce-download-link", "data"), [Input("reduce-data-btn", "n_clicks")]
)
def func(n_clicks):
    logging.critical(f"{rd_df.head(n=1)}")
    temp_path = TemporaryDirectory()
    filename = Path(temp_path.name, "reduced_data.csv")
    logging.critical(f"saving csv at {filename}")
    rd_df.to_csv(filename)
    if rd_df is not None:
        return send_file(filename.absolute())


# @app.callback(
#     dash.dependencies.Output('reduce-download-link', 'href'),
#     [dash.dependencies.Input('reduce-data', 'n_clicks')])
# def update_download_link(btn):
#     logging.critical("update_download_link() triggered")
#     if btn is not None:
#         csv_string = rd_df.to_csv(index=False, encoding='utf-8')
#         csv_string = "data:text/csv;charset=utf-8," + urllib.quote(csv_string)
#         return csv_string

if __name__ == "__main__":
    # app.run_server(debug=True)
    app.run_server(debug=True, dev_tools_ui=True, dev_tools_props_check=False)
