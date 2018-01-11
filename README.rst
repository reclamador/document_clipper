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

.. image:: https://coveralls.io/repos/github/reclamador/document_clipper/badge.svg?branch=master
     :target: https://coveralls.io/github/reclamador/document_clipper?branch=master



A set of utility classes and functions to process documents with Python


* Free software: MIT license
* Documentation: https://document-clipper.readthedocs.io.

Installation
------------

The `document_clipper` package uses libraries that relies on several command-line tools included in the
`poppler-utils` package such as:
- `pdftohtml`
- `pdfimages`
- `pftocairo`

Before attempting to use `document_clipper`, please install the `poppler-utils` package.

For instance, in Ubuntu, you may do so by running the following command:

.. code-block:: bash

    $ sudo apt-get install poppler-utils


Then, you may install `document_clipper` as usual via Python package managers, such as PIP:

.. code-block:: bash

    $ pip install document_clipper



Features
--------

* Fetch the number of pages associated to a PDF file.
* Extract the coordinates and dimensions of a given text located in a PDF file.
* Combine multiple PDFs into a single PDF.
* Combine multiple PDF **and image** files into a single PDF.
* Generate a new PDF file containing a subset of a provided source PDF file's pages. Rotations can be applied to each page individually.
* Optionally fix the document(s) involved in the slicing/merging processes beforehand.
