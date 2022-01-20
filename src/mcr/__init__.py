__version__ = "0.0.999"
"""Perform dimensional reduction and clustering on mass cytometry data
and visualize using Plotly Dash
"""
from importlib.metadata import metadata, version

try:
    __author__ = metadata(__name__)["Author"]
except KeyError:
    __author__ = "unknown"

try:
    __email__ = metadata(__name__)["Author-email"]
except KeyError:  # pragma: no cover
    __email__ = "unknown"

try:
    __version__ = version(__name__)
except KeyError:  # pragma: no cover
    __version__ = "unknown"
    
from . import cli, clustering, dash_gui, reduction