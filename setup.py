#!/usr/bin/env python

from __future__ import absolute_import
from setuptools import setup

if __name__ == '__main__':
    setup(packages=["cofdb_submit" ],
          name="cofdb-submit",
          author="Leopold Talirz",
          author_email="info@materialscloud.org",
          description="A form for uploading new CURATED COFs.",
          license="MIT",
          classifiers=["Programming Language :: Python"],
          version="0.1.0",
          install_requires=[
              "bokeh>=1.2.0",
              "jsmol-bokeh-extension>=0.2",
              "pandas",
              "panel",
              "param",
              "ipython",
              "notebook",
              "crossrefapi",
              "python-dateutil",
              "ase",
          ],
          extras_require={
              "pre-commit":
              ["pre-commit==1.17.0", "prospector==0.12.11", "pylint==1.9.3"]
          })
