================
document-clipper
================


.. image:: https://img.shields.io/pypi/v/document_clipper.svg
        :target: https://pypi.python.org/pypi/document_clipper

.. image:: https://img.shields.io/travis/reclamador/document_clipper.svg
        :target: https://travis-ci.org/reclamador/document_clipper

.. image:: https://readthedocs.org/projects/document-clipper/badge/?version=latest
        :target: https://document-clipper.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/reclamador/document_clipper/shield.svg
     :target: https://pyup.io/repos/github/reclamador/document_clipper/
     :alt: Updates


A set of utility classes and functions to process documents with Python


* Free software: MIT license
* Documentation: https://document-clipper.readthedocs.io.

Installation
------------

The `document_clipper` package uses libraries that rely on the `pdftohtml` command line util. It can be obtained by
installing the `poppler-utils` package.

For instance, in Ubuntu, run the following:

.. code-block:: bash

    $ sudo apt-get install poppler-utils


Then, you may install `document_clipper` as usual via Python package managers, such as PIP:

.. code-block:: bash

    $ pip install document_clipper



Features
--------

* Fetch the number of pages associated to a PDF file.
* Extract the coordinates and dimensions of a given text located in a PDF file.
