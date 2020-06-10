#!/usr/bin/env python
"""Load data files: cof-papers.csv and cof-frameworks.csv."""

import os
import pandas

CURATED_COFS=os.environ.get('CURATED_COFS', os.path.abspath('./CURATED-COFs'))
PAPERS_FILE = os.path.join(CURATED_COFS, 'cof-papers.csv')
FRAMEWORKS_FILE = os.path.join(CURATED_COFS, 'cof-frameworks.csv')
CIFS_FOLDER = os.path.join(CURATED_COFS, 'cifs')

try:
    PAPERS_DF = pandas.read_csv(PAPERS_FILE)
except FileNotFoundError:
    raise FileNotFoundError("ERROR: cof-papers.csv not found... check the README!")

try:
    FRAMEWORKS_DF = pandas.read_csv(FRAMEWORKS_FILE)
except FileNotFoundError:
    raise FileNotFoundError("ERROR: cof-frameworks.csv not found... check the README!")
