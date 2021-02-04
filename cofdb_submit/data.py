#!/usr/bin/env python
"""Load data files: cof-papers.csv and cof-frameworks.csv."""

import os

CURATED_COFS=os.environ.get('CURATED_COFS', os.path.abspath('./CURATED-COFs'))
PAPERS_FILE = os.path.join(CURATED_COFS, 'cof-papers.csv')
FRAMEWORKS_FILE = os.path.join(CURATED_COFS, 'cof-frameworks.csv')
CIFS_FOLDER = os.path.join(CURATED_COFS, 'cifs')