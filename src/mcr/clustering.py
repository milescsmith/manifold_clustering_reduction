from typing import Any, Dict, Optional

import logging

import igraph as ig
import leidenalg as la
import numpy as np
import pandas as pd
import scipy


# taken from scanpy._utils
def get_igraph_from_adjacency(adjacency, directed=None):
    """\
    Get igraph graph from adjacency matrix.
    """
    sources, targets = adjacency.nonzero()
    weights = adjacency[sources, targets]
    if isinstance(weights, np.matrix):
        weights = weights.A1
    g = ig.Graph(directed=directed)
    g.add_vertices(adjacency.shape[0])  # this adds adjacency.shape[0] vertices
    g.add_edges(list(zip(sources, targets)))
    g.es["weight"] = weights

    if g.vcount() != adjacency.shape[0]:
        logging.warning(
            f"The constructed graph has only {g.vcount()} nodes. "
            "Your adjacency matrix contained redundant nodes."
        )
    return g


def label_clusters(
    data_df: pd.DataFrame,
    resolution: float = 1.0,
    partition_type: la.VertexPartition.MutableVertexPartition = la.RBConfigurationVertexPartition,
    n_neighbors: int = 30,
    random_state: Optional[int] = None,
    neighbor_metric: str = "euclidean",
    neighbor_kwds: Optional[Dict[str, Any]] = None,
    neighbor_angular: bool = False,
    neighbor_verbose: bool = True,
    fuzzy_metric: str = "euclidean",
    fuzzy_metric_kwds: Optional[Dict[str, Any]] = None,
    directed_graph: bool = False,
) -> np.array:
    """\
    Given a cell-by-analyte :class:`~pd.DataFrame`, assign cluster identities
    to each cell.  Generally modeled off of the method used in :func:`~scanpy.tl.leiden`

    Parameters
    ----------
    data_df:
        :class:`pandas.DataFrame`
    resolution
        int
        default = 1.0
    partition_type:
        :class:`leidenalg.VertexPartition.MutableVertexPartition`
        default = la.RBConfigurationVertexPartition
    n_neighbors
        int
        default = 30
    random_state
        Optional[int]
        default = None
    neighbor_metric:
        str
        default = "euclidean"
    neighbor_kwds:
        Optional[Dict[str, Any]]
        default = None
    neighbor_angular:
        bool
        default = False
    neighbor_verbose
        bool
        default = True
    fuzzy_metric
        str
        default = "euclidean"
    fuzzy_metric_kwds
        Optional[Dict[str, Any]]
        default = None
    directed_graph
        bool
        default = False

    Returns
    -------
    np.array of cluster identities
    """
    from umap.umap_ import fuzzy_simplicial_set, nearest_neighbors

    logging.critical(
        f"running nearest_neighbor().  Dataset is {data_df.shape[0]} by {data_df.shape[1]}."
    )
    knn_indices, knn_distances, *_ = nearest_neighbors(
        X=data_df,
        n_neighbors=n_neighbors,
        random_state=random_state,
        metric=neighbor_metric,
        metric_kwds=neighbor_kwds,
        angular=neighbor_angular,
        verbose=neighbor_verbose,
    )

    logging.critical("running fuzzy_simplicial_set()")
    connectivities, *_ = fuzzy_simplicial_set(
        X=scipy.sparse.coo_matrix(([], ([], [])), shape=(data_df.shape[0], 1)),
        n_neighbors=n_neighbors,
        random_state=random_state,
        metric=fuzzy_metric,
        metric_kwds=fuzzy_metric_kwds,
        knn_indices=knn_indices,
        knn_dists=knn_distances,
        return_dists=True,
    )

    logging.critical("running get_igraph_from_adjacency()")
    g = get_igraph_from_adjacency(connectivities, directed=directed_graph)

    logging.critical("running find_partition()")
    partition = la.find_partition(
        graph=g, partition_type=partition_type, resolution_parameter=resolution
    )

    return np.array(partition.membership)
