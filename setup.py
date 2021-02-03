#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import io
import re
from glob import glob
from os.path import join
from pathlib import Path

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    with io.open(
        join(Path(__file__).parent, *names), encoding=kwargs.get("encoding", "utf8")
    ) as fh:
        return fh.read()


setup(
    name="mass-cytometry-reduction",
    use_scm_version={
        "local_scheme": "dirty-tag",
        "write_to": "src/mcr/_version.py",
        "fallback_version": "0.0.999",
    },
    license="LGPL-3.0-or-later",
    description="Perform UMAP on mass cytometry data and visualize using Plotly Dash",
    long_description="%s\n%s"
    % (
        re.compile("^.. start-badges.*^.. end-badges", re.M | re.S).sub(
            "", read("README.rst")
        ),
        re.sub(":[a-z]+:`~?(.*?)`", r"``\1``", read("CHANGELOG.rst")),
    ),
    author="Miles Smith",
    author_email="miles-smith@omrf.org",
    url="https://github.com/milescsmith/mass_cytometry_reduction",
    packages=find_packages("src"),
    package_dir={"mcr": "src/mcr"},
    py_modules=[Path(path).stem for path in glob("src/mcr/*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)"
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        # uncomment if you test on these interpreters:
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: Stackless',
        "Topic :: Utilities",
    ],
    project_urls={
        "Documentation": "https://mass_cytometry_reduction.readthedocs.io/",
        "Changelog": "https://mass_cytometry_reduction.readthedocs.io/en/latest/changelog.html",
        "Issue Tracker": "https://github.com/milescsmith/mass_cytometry_reduction/issues",
    },
    keywords=[
        "mass cytometry",
        "umap",
        "tsne"
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    python_requires=">=3.7",
    install_requires=[
        line.strip()
        for line in Path("requirements.txt").read_text("utf-8").splitlines()
    ],
    extras_require={
        "tf": ["tensoflow>=2.3.0"],
        "forceatlas2": ["fa2"],
        "openTSNE": ["opentsne~=0.5"],
        "pacmap": ["pacmap~=0.2"],
        "optsne": ["git+https://github.com/omiq-ai/Multicore-opt-SNE"],
        "all_dr": [
            "fa2",
            "opentsne~=0.5",
            "pacmap~=0.2",
            "git+https://github.com/omiq-ai/Multicore-opt-SNE",
        ],
        "dash": [
            "dash~=1.19",
            "dash_table~=4.11",
            "dash_bootstrap_components~=0.11",
            "dash_core_components~=1.15",
            "dash_daq~=0.5",
            "dash_extensions~=0.0.4",
            "dash_html_components~=1.1",
        ],
        "all": [
            "fa2",
            "opentsne~=0.5",
            "pacmap~=0.2",
            "git+https://github.com/omiq-ai/Multicore-opt-SNE",
            "dash~=1.19",
            "dash_table~=4.11",
            "dash_bootstrap_components~=0.11",
            "dash_core_components~=1.15",
            "dash_daq~=0.5",
            "dash_extensions~=0.0.4",
            "dash_html_components~=1.1",
        ],
    },
    setup_requires=[
        "pytest-runner",
        "setuptools_scm>=3.3.1",
    ],
    entry_points={
        "console_scripts": [
            "mcr = mcr.cli:main",
        ]
    },
)
