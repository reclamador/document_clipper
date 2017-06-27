#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


requirements = [
    'beautifulsoup4==4.3.2',
    'lxml==3.3.2',
    'scraperwiki==0.5.1'
]

setup_requirements = []

test_requirements = []

setup(
    name='document_clipper',
    version='0.1.0',
    description="A set of utility classes and functions to process documents with Python",
    long_description=readme + '\n\n' + history,
    author="Nick Jaremek",
    author_email='nick13jaremek@gmail.com',
    url='https://github.com/reclamador/document_clipper',
    packages=find_packages(include=['document_clipper']),
    include_package_data=True,
    install_requires=requirements,
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
