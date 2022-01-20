========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - |
        | |coveralls| |codecov|
        | |codacy|
    * - package
      - | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/mass_cytometry_reduction/badge/?style=flat
    :target: https://readthedocs.org/projects/mass_cytometry_reduction
    :alt: Documentation Status

.. |coveralls| image:: https://coveralls.io/repos/milescsmith/mass_cytometry_reduction/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/milescsmith/mass_cytometry_reduction

.. |codecov| image:: https://codecov.io/gh/milescsmith/mass_cytometry_reduction/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/milescsmith/mass_cytometry_reduction

.. |codacy| image:: https://app.codacy.com/project/badge/Grade/2e69c07714324a33a57d221deb4865d0
    :target: https://www.codacy.com/gh/milescsmith/mass_cytometry_reduction/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=milescsmith/mass_cytometry_reduction&amp;utm_campaign=Badge_Grade
    :alt: Codacy Code Quality Status

.. |commits-since| image:: https://img.shields.io/github/commits-since/milescsmith/mass_cytometry_reduction/v0.0.999.svg
    :alt: Commits since latest release
    :target: https://github.com/milescsmith/mass_cytometry_reduction/compare/v0.0.999...master



.. end-badges

Perform dimensional reduction and clustering on mass cytometry data and visualize using Plotly Dash

* Free software: GNU Lesser General Public License v3 or later (LGPLv3+)

Installation
============

::

    pip install mass-cytometry-reduction

You can also install the in-development version with::

    pip install https://github.com/milescsmith/mass_cytometry_reduction/archive/master.zip


Documentation
=============


https://mass_cytometry_reduction.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
