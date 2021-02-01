"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mmass_cytometry_reduction` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``mass_cytometry_reduction.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``mass_cytometry_reduction.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""

from pathlib import Path
from typing import Optional
import logging
import click
import pandas as pd

# import numpy as np
from umap import UMAP
from sklearn.manifold import TSNE  # replace this with Opt-SNE and/or openTSNE

# add forceatlas2? PaCMAP? Somehow work in PAGA?


def setup_logging(name: Optional[str] = None):
    if name:
        logger = logging.getLogger(name)
    else:
        logger = logging.getLogger(__name__)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if name:
        fh = logging.FileHandler(filename=name)
    else:
        fh = logging.FileHandler(filename=f"{__name__}.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    st = logging.StreamHandler()
    st.setLevel(logging.INFO)
    st.setFormatter(formatter)
    logger.addHandler(st)


@click.group()
def main():
    setup_logging("mcr")


def read_data(filename: str) -> Optional[pd.DataFrame]:
    """
    Read in csv or excel file containing data.
    """

    # This is just here because I cannot rely on people giving me a csv
    # no matter how many times I tell them Excel is crap

    datafile = Path(filename)

    if datafile.suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(datafile)
    elif datafile.suffix == ".csv":
        df = pd.read_csv(datafile)
    else:
        logging.error(
            "That file type is unknown.  Please provide a CSV, XLSX, or XLS file to use."
        )
        return None

    return df


def perform_reducion(
    df: pd.DataFrame,
    reduction: str = "umap",
) -> pd.DataFrame:

    if reduction == "umap":
        embeddings = UMAP().fit_transform(df)
        embeddings_df = pd.DataFrame(embeddings).rename(
            columns={0: "umap_1", 1: "umap_2"}
        )
    elif reduction == "tsne":
        embeddings = TSNE().fit_transform(df)
        embeddings_df = pd.DataFrame(embeddings).rename(
            columns={0: "tsne_1", 1: "tsne_2"}
        )
    else:
        logging.error("That is not a recognized dimensional reduction algorithm")
        raise Exception

    return embeddings_df


@main.command()
@click.option(
    "--data_file",
    help="File containing antigen expression",
    type=str,
    default=None,
    show_default=True,
    required=True,
)
@click.option(
    "--reduction",
    hep=(
        "Type of dimensional reduction to perform.  "
        "Choices include 'UMAP', 'Parametric UMAP (pumap)', and 'tSNE'"
    ),
    type=click.Choice(["umap", "pumap", "tsne"]),
    default="umap",
    show_default=True,
    required=False,
)
@click.option(
    "--cluster",
    help=(
        "Perform clustering on the data in addition to "
        "running the chosen dimensional reduction"
    ),
    type=bool,
    default=False,
    show_default=True,
    is_flag=True,
)
@click.option(
    "--ignore_columns",
    help=(
        "A list of columns (seperated by commas) in the `data_file` to "
        "ignore.  Generally stuff like cell name or size or anything that "
        "might be irrelvant"
    ),
    type=str,
    default=(
        "Object Id,XMin,XMax,YMin,YMax,Cell Area (µm²),Cytoplasm Area (µm²),"
        "Membrane Area (µm²),Nucleus Area (µm²),Nucleus Perimeter (µm),"
        "Nucleus Roundness"
    ),
    show_default=True,
    required=False,
)
@click.option(
    "--output",
    help="Filename to write results to",
    type=str,
    default="output.csv",
    show_default=True,
    required=False,
)
def reduce_data(
    data_file: str,
    output: str,
    reduction: str = "umap",
    cluster: bool = False,
    ignore_columns: Optional[str] = None,
):
    """Perform dimensional reduction on mass cytometry data"""
    df = read_data(data_file)

    if ignore_columns:
        original_df = df
        df = df.loc[:, ~df.columns.isin(ignore_columns.split(","))]
    else:
        original_df = df

    processed_data = perform_reducion(df, reduction)

    combined_data = pd.concat(
        [original_df.reset_index(drop=True), processed_data], axis=1
    )
    combined_data.to_csv(output)
