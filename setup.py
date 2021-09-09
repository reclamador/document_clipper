#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


requirements = [
    'beautifulsoup4==4.4.1',
    'lxml==4.2.5',
    'pilkit==2.0',
    'PyPDF2==1.26.0',
    'Pillow==4.2.1',
]

setup_requirements = []

test_requirements = [
    'mock==2.0.0'
]

setup(
    name='document_clipper',
    version='1.2.1',
    description="A set of utility classes and functions to process documents with Python",
    long_description=readme + '\n\n' + history,
    author="Nick Jaremek",
    author_email='nick13jaremek@gmail.com',
    url='https://github.com/reclamador/document_clipper',
    packages=[
        'document_clipper'
    ],
    include_package_data=True,
    install_requires=requirements,
    dependency_links=[
        "-git+ssh://git@github.com/scraperwiki/scraperwiki-python#egg=scraperwiki"
    ],
    license="MIT license",
    zip_safe=False,
    keywords='document_clipper',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
