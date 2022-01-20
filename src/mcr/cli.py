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

from typing import Optional

import logging
from copy import deepcopy
from pathlib import Path

import click
import numpy as np
import pandas as pd

from .clustering import label_clusters
from .reduction import perform_reducion


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


def read_data(filename: str) -> Optional[pd.DataFrame]:
    """
    Read in csv or excel file containing data.
    """

    # This is just here because I cannot rely on people giving me a csv
    # no matter how many times I tell them Excel is crap

    datafile = Path(filename)

    if datafile.suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(datafile)
    elif datafile.suffix in [".csv", ".tsv", ".txt"]:
        df = pd.read_csv(datafile, engine="python")
    else:
        logging.error(
            "That file type is unknown.  Please provide a CSV, XLSX, or XLS file to use."
        )
        return None

    return df


@click.group()
def main():
    setup_logging("mcr")


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
    help=(
        "Type of dimensional reduction to perform.  "
        "Choices include 'UMAP', 'Parametric UMAP (pumap)', 'tSNE' (using the "
        "scikit-learn implementation), 'opt-SNE', or 'open-TSNE"
    ),
    type=click.Choice(["umap", "pumap", "tsne", "pacmap", "openTSNE", "optsne"]),
    default="umap",
    show_default=True,
    required=False,
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
    ignore_columns: Optional[str] = None,
    add_to_source: bool = False,
    **kwargs,
) -> None:
    """Perform dimensional reduction on mass cytometry data
    \f
    Parameters
    ----------
    \f
    Returns
    -------
    """
    df: pd.DataFrame = read_data(data_file)

    original_df: pd.DataFrame = deepcopy(df)
    if ignore_columns:
        df = df.loc[:, ~df.columns.isin(ignore_columns.split(","))]

    processed_data = perform_reducion(df, reduction, **kwargs)

    if add_to_source:
        combined_data = pd.concat(
            [original_df.reset_index(drop=True), processed_data], axis=1
        )
        combined_data.to_csv(output)
    else:
        processed_data.to_csv(output)


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
    "--output",
    help="Filename to write results to",
    type=str,
    default="output.csv",
    show_default=True,
    required=False,
)
@click.option(
    "--cluster_name",
    help="Name to use for cluster column added to data file",
    type=str,
    default=None,
    show_default=False,
    required=False,
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
    "--add_to_source",
    help=(
        "If true, cluster identities are added as a column to the original data;"
        "if false, clustering identities alone are saved."
    ),
    type=bool,
    default=True,
    show_default=True,
    required=False,
)
def cluster_cells(
    data_file: str,
    output: str,
    cluster_name: Optional[str] = None,
    resolution: float = 0.6,
    ignore_columns: Optional[str] = None,
    add_to_source: bool = False,
    **kwargs,
) -> None:
    """Identify clusters in mass cytometry data
    \f
    Parameters
    ----------
    data_file : `str`
        A delimited or Excel spreadsheet containing data to analyze.
        Must be in the format where cells are in rows and analytes are in columns.
    output : `str`
        File to write results to
    cluster_name : `str`, optional (default: `res_X`, where `X` is the resolution)
        Name to give column where the cluster identities are written
    resolution : `float` (default: `0.6`)
        Sensitivity at which to search for clusters.  Lower numbers result in few clusters,
        while a higher number yields many clusters, though at some point ever cell becomes
        its own clusters.Typically between 0.2 and 2.
    ignore_columns : `str` (default: `"Object Id,XMin,XMax,YMin,YMax,Cell Area (µm²),Cytoplasm Area (µm²),"
        "Membrane Area (µm²),Nucleus Area (µm²),Nucleus Perimeter (µm),"
        "Nucleus Roundness"1)
        A list of columns in the `data_file` to ignore when performing clustering.  For instance,
        "Object Id", or "Cell Area".
    add_to_source : `bool`, (default: `False`)
        Return the cluster information added as a new column in the original table.
    **kwargs :
        Additional arguments to pass to the :func:`~nearest_neighbors` or
        :func:`~fuzzy_simplicial_set` functions.

    \f
    Returns
    -------
    `None`
        If `add_to_source` is false, writes results to a single column CSV;
        if `add_to_source` is true, writes results to a new column appened to
        the input dataframe.
    """
    df: pd.DataFrame = read_data(data_file)

    if not cluster_name:
        cluster_name = f"res_{resolution}"

    original_df: pd.DataFrame = deepcopy(df)
    if ignore_columns:
        df = df.loc[:, ~df.columns.isin(ignore_columns.split(","))]

    clusters = label_clusters(data_df=df, resolution=resolution, **kwargs)

    if add_to_source:
        original_df[cluster_name] = clusters
        original_df.to_csv(output, index=False)
    else:
        np.savetxt(fname=output, X=clusters.astype(int), fmt="%i")
