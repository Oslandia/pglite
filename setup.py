#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='pglite',
    version='1.0.2',
    description="PostgreSQLite",
    long_description="PostgreSQLite - a simple postgresql cluster",
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Database :: Front-Ends",
        "Topic :: System :: Software Distribution",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    keywords='postgresql,pglite',
    author='Oslandia',
    author_email='infos@oslandia.com',
    maintainer='Oslandia',
    maintainer_email='infos@oslandia.com',

    license='LGPL',
    packages=['pglite'],
    include_package_data=True,
    zip_safe=False,
    install_requires=(),
    extras_require={
        "develop": ()
    },

    entry_points=dict(console_scripts=[
        'pglite=pglite.pglite:main',
    ]),
)
