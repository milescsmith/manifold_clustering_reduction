import logging

import pandas as pd

# add Opt-SNE and/or openTSNE
# add forceatlas2? Somehow work in PAGA?


def perform_reducion(
    df: pd.DataFrame, reduction: str = "umap", **kwargs
) -> pd.DataFrame:

    if reduction == "umap":
        from umap import UMAP

        embeddings = UMAP(**kwargs).fit_transform(df)
    elif reduction == "tsne":
        from sklearn.manifold import TSNE

        embeddings = TSNE(**kwargs).fit_transform(df)
    elif reduction == "openTSNE":
        try:
            from openTSNE import TSNE

            embeddings = TSNE(**kwargs).fit(df.values)
        except ImportError as error:
            logging.error(
                "The openTSNE module is not available.  Please ensure it is installed"
            )
    # elif reduction == "optTSNE":
    #     try:
    #         from MulticoreTSNE import MulticoreTSNE

    #         embeddings = MulticoreTSNE(**kwargs).fit_transform(df)
    #     except ImportError as error:
    #         logging.error(
    #             "The opt-SNE module is not available.  Please ensure it is installed"
    #         )
    elif reduction == "pacmap":
        try:
            from pacmap import PaCMAP

            embeddings = PaCMAP(
                n_dims=2, n_neighbors=None, MN_ratio=0.5, FP_ratio=2.0
            ).fit_transform(df.values)
        except ImportError as error:
            logging.error(
                "The PaCMAP module is not available.  Please ensure it is installed"
            )
    else:
        logging.error("That is not a recognized dimensional reduction algorithm")
        raise Exception

    return pd.DataFrame(embeddings).rename(
        columns={x: f"{reduction}_{x+1}" for x in range(embeddings.shape[1])}
    )
