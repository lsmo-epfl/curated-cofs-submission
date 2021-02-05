#!/usr/bin/env python
"""Add new entries to the CURATED-COFs files: cof-papers.csv and cof-frameworks.csv."""

import os
import numpy as np
import panel as pn
import datetime
import pandas as pd
from data import PAPERS_FILE, FRAMEWORKS_FILE, CIFS_FOLDER

def get_papers_df():
    try:
        papers_df = pd.read_csv(PAPERS_FILE) # needs to be loaded each time, to have the last entries!
    except FileNotFoundError:
        raise FileNotFoundError("ERROR: cof-papers.csv not found... check the README!")
    return papers_df

def get_frameworks_df():
    try:
        frameworks_df = pd.read_csv(FRAMEWORKS_FILE) # needs to be loaded each time, to have the last entries!
    except FileNotFoundError:
        raise FileNotFoundError("ERROR: cof-frameworks.csv not found... check the README!")
    return frameworks_df

def mint_paper_id(doi, year):
    """Check if the paper is already in cof-papers.csv (same DOI) and print that value,
    otherwise assign the new paper ID.
    """

    papers_df = get_papers_df()

    if doi in papers_df['DOI'].values:
        return str(papers_df[papers_df['DOI'] == doi]['CURATED-COFs paper ID'].values[0]) + " (already present)"

    id_year = sorted(papers_df[papers_df['CURATED-COFs paper ID'].str.contains("p"+year[2:])]['CURATED-COFs paper ID'])
    if len(id_year)==0:
        counter = 0
    else:
        last_id_year = id_year[-1]
        last_counter_year = int(last_id_year[3:5])
        counter = last_counter_year + 1

    return "p{:s}{:02d}".format(year[2:], counter)

def mint_cof_id(paper_id, charge, dimensionality):
    """Check the list of CURATED-COF IDs and assign a new one accordingly."""

    frameworks_df = get_frameworks_df()
    other_cofs = [ id for id in frameworks_df["CURATED-COFs ID"] if id.startswith(paper_id[1:])]
    counter = len(other_cofs)
    return "{paper}{counter}{charge}{dim}".format(paper=paper_id[1:], counter=str(counter), charge=charge,
                                                  dim=dimensionality)

pn.extension()

inp_doi = pn.widgets.TextInput(name='Publication DOI', placeholder="10.1021/jacs.9b01891")
btn_doi = pn.widgets.Button(name='Fetch metadata', button_type='primary')

inp_reference = pn.widgets.TextInput(name='Publication reference', placeholder='')
inp_title = pn.widgets.TextInput(name='Publication title', placeholder='')
inp_year = pn.widgets.TextInput(name='Publication year', placeholder='')
inp_paper_id = pn.widgets.TextInput(name='CURATED-COFs paper ID', placeholder='')

div_out = pn.widgets.StaticText(name='Output', value='')
btn_add_paper = pn.widgets.Button(name='Add paper', button_type='primary')

def on_click_fetch(event):
    """Get metadata for DOI, and return an error if the DOI is not valid (no metadata found)."""
    import dateutil
    from crossref.restful import Works
    import json

    # turn the "Add paper" primary, to remember clicking it again!
    btn_add_paper.button_type = 'primary'

    # test data
    inp_doi.value = inp_doi.value or "10.1021/jacs.9b01891"

    works = Works()
    print("Querying Crossref API for doi {}".format(inp_doi.value))
    metadata = works.doi(inp_doi.value)
    #print(json.dumps(metadata,sort_keys=True, indent=4))

    if not metadata:
        btn_doi.button_type = 'danger'
        inp_title.value = inp_year.value = inp_reference.value = inp_paper_id.value = "ERROR: wrong/missing DOI."
        return

    inp_title.value = str(metadata['title'][0])
    journal = str(metadata['short-container-title'][0])

    if 'volume' in metadata:
        already_in_issue = True
        volume = metadata['volume']
        if 'published-print' in metadata: # ACS, wiley
            year = str(metadata['published-print']['date-parts'][0][0])
        elif 'created' in metadata: # RSC
            year = str(metadata['created']['date-parts'][0][0])
        else:
            year = 'ERROR: year not found.'
    else: # not yet in an issue: assuming that it will be published at the same year of today
        already_in_issue = False
        year = str(datetime.datetime.now().year)

    inp_year.value = year

    if already_in_issue:
        if 'page' in metadata: # most of the journals
            inp_reference.value = "{}, {}, {}, {}".format(journal, year, volume, metadata['page'])
        else:  # NatComm or not yet in an issue
            inp_reference.value = "{}, {}, {}".format(journal, year, volume)
    else:
        inp_reference.value = "{}, {}, {}".format(journal, year, "in press")
    inp_paper_id.value = mint_paper_id(doi=inp_doi.value, year=inp_year.value)
    btn_doi.button_type = 'success'

btn_doi.on_click(on_click_fetch)

def on_click_add(event):
    """Add paper to file cof-papers.csv: botton will turn red if something is missing or paper already present."""
    if not (inp_paper_id.value and inp_reference.value and inp_doi.value and inp_title.value) or \
       "(already present)" in inp_paper_id.value or \
       "ERROR" in inp_paper_id.value:
        btn_add_paper.button_type = 'danger'
        print(inp_paper_id.value + " Paper not added because of some problem.")
        return

    btn_add_paper.button_type = 'primary'

    line = '{id},"{ref}",{doi},"{title}"\n'.format(id=inp_paper_id.value, ref=inp_reference.value,
                                                  doi=inp_doi.value, title=inp_title.value)
    print(line)
    with open(PAPERS_FILE, 'a+') as handle:
        handle.write(line)

    btn_add_paper.button_type = 'success'

btn_add_paper.on_click(on_click_add)

column = pn.Column(
    pn.pane.HTML("""<h2>Add Paper</h2>"""),
    pn.Row(inp_doi, btn_doi),
    inp_title,
    inp_year,
    inp_reference,
    inp_paper_id,
    btn_add_paper,
)

column.servable()

"""Add CIF info"""
"CURATED-COFs ID","Source","Name","Elements","Modifications"
"05000N2","tong-v2, 035","COF-1","H,B,C,O","Science, 2005, 310, 1166-1170","none","none"

class CifForm():
    """Input form for CIF file"""

    def __init__(self):
        self.inp_cif = pn.widgets.FileInput(name='CIF', accept='.cif')
        self.btn_cif = pn.widgets.Button(name='Parse CIF', button_type='primary')
        self.btn_cif.on_click(self.on_click_parse)
        self.ckbox_2x = pn.widgets.Checkbox(name='Force to replicate 2x in C direction')
        self.ckbox_rot_zxy = pn.widgets.Checkbox(name='Rotate axes xyz to zxy')
        self.ckbox_rot_yzx = pn.widgets.Checkbox(name='Rotate axes xyz to yxz')

        from structure import structure_jsmol
        import bokeh.models as bmd
        self.jsmol_script_source = bmd.ColumnDataSource()
        self.applet = structure_jsmol(self.jsmol_script_source)

        self.inp_source = pn.widgets.Select(name='CIF source', 
            options={'SI': 'SI', 
                     'SI (CIF)': 'SI (CIF)', 
                     'CSD': 'CSD',
                     'Private Communication': "Priv. Comm."})
        self.inp_csd = pn.widgets.TextInput(name='CSD Number', placeholder='1846139')
        self.inp_name = pn.widgets.TextInput(name='CIF name', placeholder='As used in publication')
        self.inp_dimensionality = pn.widgets.TextInput(name='CIF dimensionality', placeholder='Detected by ASE')
        self.inp_elements = pn.widgets.TextInput(name='CIF elements', placeholder='C,H,...')
        self.inp_modifications = pn.widgets.AutocompleteInput(
            name='CIF modifications', value='none', 
            options=list(set(get_frameworks_df()['Modifications'])), restrict=False)
        self.inp_charge = pn.widgets.Select(name='CIF charge', options={ 'Neutral': 'N', 'Charged': 'C' })
        self.inp_cof_id = pn.widgets.TextInput(name='COF ID', value='none')
        self.btn_mint_id = pn.widgets.Button(name='Mint', button_type='primary')
        self.btn_mint_id.on_click(self.mint_framework_id)

        self.btn_add_cif = pn.widgets.Button(name='Add CIF', button_type='primary')
        self.btn_add_cif.on_click(self.on_click_add)

    @property
    def info_dict(self):
        """Dictionary containing all the information assigned (automatically or manually) for the new COF."""
        if self.inp_source.value == "CSD":
            source = "CSD, {}".format(self.inp_csd.value)
        else:
            source = self.inp_source.value
        return {
            'cof_id': self.inp_cof_id.value,
            'source': source,
            'name': self.inp_name.value,
            'dimensionality': self.inp_dimensionality.value,
            'elements': self.inp_elements.value,
            'modifications': self.inp_modifications.value,
            'charge': self.inp_charge.value,
        }

    def servable(self):
        """Layout of the CIF section of the page."""
        self.column = pn.Column(
            pn.pane.HTML("""<h2>Add CIF</h2>"""),
            pn.Row(
                self.inp_cif, 
                pn.Column(
                    self.btn_cif,
                    self.ckbox_rot_zxy,
                    self.ckbox_rot_yzx,
                    self.ckbox_2x
                )
            ),
            pn.pane.Bokeh(self.applet),
            pn.Row(self.inp_source, self.inp_csd),
            self.inp_name,
            self.inp_dimensionality,
            self.inp_elements,
            self.inp_modifications,
            self.inp_charge,
            pn.Row(self.inp_cof_id, self.btn_mint_id),
            self.btn_add_cif,
        )
        return self.column.servable()

    def on_click_parse(self, event):
        """Load the CIF, unwrap it to P1 using ASE, extract some info, and display it."""
        from ase.io import read, write
        from ase.io.cif import write_cif
        from ase.geometry.dimensionality import analyze_dimensionality
        from ase.build import make_supercell
        from io import StringIO, BytesIO
        import re

        # turn "Add CIF" button primary, to remember clicking it again!
        self.btn_add_cif.button_type = 'primary'

        # assign the filename as the first guess for the COF name, which can be manually corrected
        self.inp_name.value = self.inp_cif.filename.split(".")[0]

        # read the CIF file and get useful information
        cif_str = self.inp_cif.value.decode()
        print(self.inp_cif.get_param_values())
        atoms = read(StringIO(cif_str), format='cif')

        formula = atoms.get_chemical_formula()
        elements = [e for e in re.split(r'\d+', formula) if e]
        self.inp_elements.value = ",".join(elements)
        self.inp_modifications.value = 'none'

        # If the user selects the proper checkbox, rotate the cell
        if self.ckbox_rot_zxy.value:
            print("USER CHOICE: rotate axis to ZXY")
            cell = atoms.cell
            atoms.set_cell([ cell[2], cell[0], cell[1] ])
        if self.ckbox_rot_yzx.value:
            print("USER CHOICE: rotate axis to YZX")
            cell = atoms.cell
            atoms.set_cell([ cell[1], cell[2], cell[0] ])

        # If the 2x replication was chosen go with that, otherwise check first if there is the need
        # NOTE: this is usefull because sometime the layers are close by and ASE recognizes it as a 3D frameworks,
        #       but you want to force the choice of assuming it is a 2D COF and need 2 layers

        if self.ckbox_2x.value:
            print("USER CHOICE: force the frameworks to be 2D and duplicate 2x in C direction")
            self.inp_dimensionality.value = '2D'
            atoms = make_supercell(atoms, np.diag([1,1,2]))
            self.inp_modifications.value = 'replicated 2x in C direction'
        else:
            intervals = analyze_dimensionality(atoms, method='RDA')
            if intervals[0].dimtype == '2D':
                self.inp_dimensionality.value = '2D'

                # Check if it is correcly oriented, and extend to two layers if onyly one is present
                z_min_thr = 6 #if less, it is likely a single layer
                cell_lengths = atoms.get_cell_lengths_and_angles()[0:3]
                if cell_lengths[0] < z_min_thr or cell_lengths[1] < z_min_thr: # X or Y are perpendicular the layer
                    self.inp_dimensionality.value = "ERROR: you need to rotate the axes to have the layers on XY plane."
                    self.inp_modifications.value = "ERROR: you need to rotate the axes to have the layers on XY plane."
                if cell_lengths[2] < z_min_thr: # Z is perpendicular to a single layer
                    atoms = make_supercell(atoms, np.diag([1,1,2]))
                    self.inp_modifications.value = 'replicated 2x in C direction'
            else:
                self.inp_dimensionality.value = '3D'

        self.atoms = atoms
        import tempfile
        with tempfile.TemporaryFile() as handle:
            write(handle, atoms, format='cif')
            handle.seek(0)
            self.cif_str = handle.read()

        self.display(self.cif_str.decode())


    def on_click_add(self, event):
        """Add framework to list and add CIF file to cifs/ folder."""
        from ase.io import write
        info = self.info_dict
        if not all(v for k,v in info.items() if k not in ['modifications']):
            self.btn_add_cif.button_type = 'danger'
            return

        self.btn_add_cif.button_type = 'primary'
        line = '{id},{source},"{name}","{elements}","{mod}"\n'.format(
            id=info['cof_id'], source=info['source'], name=info['name'], elements = info['elements'],
            mod=info['modifications'])
        print(line)
        with open(FRAMEWORKS_FILE, 'a+') as handle:
           handle.write(line)

        cif_path = os.path.join(CIFS_FOLDER, info['cof_id'] + '.cif')

        print("Writing {}".format(cif_path))
        write(cif_path, self.atoms)

        # Using manage_crystal to use the standard formatting
        from manage_crystal.utils import parse_and_write
        parse_and_write(cif_path, cif_path)

        self.btn_add_cif.button_type = 'success'

    def mint_framework_id(self, event):
        """Get the paper id, and warn if not paper info is given."""
        if not inp_paper_id.value:
            self.inp_cof_id.value = "ERROR: add DOI of the paper first."
            return
        # Remove "(already present)" if present
        paper_id = inp_paper_id.value.split()[0]
        self.inp_cof_id.value = mint_cof_id(paper_id, self.inp_charge.value, self.inp_dimensionality.value[0])

    def display(self, cif_str):
        """Update applet to show CIF."""
        from structure import structure_jsmol

        self.jsmol_script_source.data['script'] = [
"""load data "cifstring"
{}
end "cifstring"
""".format(str(cif_str))]
        #print(self.jsmol_script_source.data['script'])


cif = CifForm()
cif.servable()
