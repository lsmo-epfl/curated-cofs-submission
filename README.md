# CURATED COFs Upload form

This is an interactive upload form for contributing new entries to the [CURATED COFs database](https://github.com/danieleongari/CURATED-COFs).

The form is written using [panel](https://panel.pyviz.org/) and uses the [jsmol-bokeh-extension](https://github.com/ltalirz/jsmol-bokeh-extension)

The package included two interactive forms: `parse_cif` and `cofdb_submit`

## Utility `parse_cif`

This is a general purpose utility to help in the creation of the CIF files, by copy&paste of the information as usually reported in the Supporting PDF of a synthesis paper. The CIF file gets printed in the `cifs` directory, using the input name of the material as filename, and keeping the original symmetry unwrapped.

## Features of `cofdb_submit`

Papers:
 * Fetch publication metadata from DOI
 * Mint CURATED-COFS paper ID
 * Add info to .csv

Frameworks:
 * Select the file or drag it to the `Choose file` button
 * Relabel axes to keep the 2D layers parallel to the `ab` plane
 * Replicate 2D COFs in `c` direction to include 2 layers 
 * Render CIF using jsmol
 * Prefill basic information (name, elements, 2D/3D)
 * Mint CURATED-COFS framework ID
 * Add info to .csv and add new CIF, with unwrapped P1 symmetry

## Prerequisites

 * nodejs >= 10

## Installation

```
git clone https://github.com/ltalirz/curated-cofs-submission.git
pip install -r requirements.txt
```

Add path to clone of CURATED-COFs github repository and run it in your browser at http://localhost:5006/cofdb_submit.

```
export CURATED_COFS=/path/to/CURATED-COFs
bokeh serve cofdb_submit/ --show
```

## Development
```
# enable live reloading when changing the code
panel serve  cofdb_submit/ --dev cofdb_submit/main.ipynb
```

## Online version
Playing around with deployment of this app on heroku [here](https://ltal-py.herokuapp.com)
