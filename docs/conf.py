# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import traceback

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.ifconfig",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
]
source_suffix = ".rst"
master_doc = "index"
project = "mass_cytometry_reduction"
year = "2021"
author = "Miles Smith"
copyright = "{0}, {1}".format(year, author)
try:
    from pkg_resources import get_distribution

    version = release = get_distribution("mass_cytometry_reduction").version
except Exception:
    traceback.print_exc()
    version = release = "0.0.999"

pygments_style = "trac"
templates_path = ["."]
extlinks = {
    "issue": (
        "https://github.com/milescsmith/mass_cytometry_reduction/issues/%s",
        "#",
    ),
    "pr": (
        "https://github.com/milescsmith/mass_cytometry_reduction/pull/%s",
        "PR #",
    ),
}
# on_rtd is whether we are on readthedocs.org
on_rtd = os.environ.get("READTHEDOCS", None) == "True"

if not on_rtd:  # only set the theme if we're building docs locally
    html_theme = "sphinx_rtd_theme"

html_use_smartypants = True
html_last_updated_fmt = "%b %d, %Y"
html_split_index = False
html_sidebars = {
    "**": ["searchbox.html", "globaltoc.html", "sourcelink.html"],
}
html_short_title = "%s-%s" % (project, version)

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False
