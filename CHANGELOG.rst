
Changelog
=========

0.3.1 (2021-02-04)
--------------------

Added:
......

* `environment.yml` to assist in installing, especially in restricted environments or on Windows

* Add import of `click` to `dash_gui.py`

Changed:
........

* Renamed to `manifold clustering and reduction`

* Updated a few incorrect items in `requirements.txt`

0.3.0 (2021-02-03)
--------------------

Added:
......

* Added a GUI interface using Plotly Dash.
* Added handlers to perform reductions with opt-SNE, open-TSNE, and PaCMAP.

0.2.0 (2021-02-02)
--------------------

Changed:
........

* Moved UMAP and other method imports into functions where they are used. 

  * UMAP import, especially caused very slow overall startup

0.1.9 (2021-01-31)
--------------------

* Add notebook with experiments figureing out leiden clustering
* Add module with clustering functions.

0.1.0 (2021-01-30)
--------------------

* First version capable of ingesting data, performing dimensional reduction,
  and writing results to file.

0.0.9 (2021-01-29)
--------------------

* First commit.
