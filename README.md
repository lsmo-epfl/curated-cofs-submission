# CURATED COFs Upload form

This is an interactive upload form for contributing new entries to the [CURATED COFs database](https://github.com/danieleongari/CURATED-COFs).

The form is written using [panel](https://panel.pyviz.org/) and uses the [jsmol-bokeh-extension](https://github.com/ltalirz/jsmol-bokeh-extension)

## Features

Papers:
 * Fetch publication metadata from DOI
 * Mint CURATED-COFS paper ID
 * Add info to .csv

Frameworks:
 * Render CIF using jsmol
 * Prefill basic information (elements)
 * Mint CURATED-COFS framework ID
 * Add info to .csv and add new CIF

Possible future extensions:
 * adding hydrogens automatically?
 * automatic orientation?
 * ... your idea here!

## Installation

```
git clone https://github.com/ltalirz/curated-cofs-submission.git
pip install -r requirements.txt
# add path to clone of CURATED-COFs github repository
export CURATED_COFS=/path/to/CURATED-COFs
bokeh serve cofdb_submit/
```
Open http://localhost:5006/cofdb_submit in your browser.

## Development
```
# enable live reloading when changing the code
panel serve  cofdb_submit/ --dev cofdb_submit/main.ipynb
```

## Online version
Playing around with deployment of this app on heroku [here](https://ltal-py.herokuapp.com)
