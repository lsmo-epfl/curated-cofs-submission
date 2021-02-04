#!/usr/bin/env python
"""Add new entries to the CURATED-COFs files: cof-papers.csv and cof-frameworks.csv."""

import os
import numpy as np
import panel as pn
import pandas as pd
import datetime
import re
from pathlib import Path

pn.extension()

class CifParse():
    """Input form for CIF file"""

    def __init__(self):
        self.name_input = pn.widgets.TextInput(name='COF name', placeholder='Insert...')
        self.cell_input = pn.widgets.TextInput(name='Cell info', placeholder='a = b = 37.2145 37.2145 Å , c = 4.0878 Å, α = β = 90° 90 and γ = 120°')
        self.symm_input = pn.widgets.TextInput(name='Symm info', placeholder='P6 (check the table on the bottom)')
        self.coord_input = pn.widgets.input.TextAreaInput(
            name='Atomic coord. info', 
            placeholder='Enter a string here...', 
            max_length=100000,
            height=800,
            )
        self.find = pn.widgets.TextInput(name='Find', placeholder='RegEx to find...')
        self.replace = pn.widgets.TextInput(name='Replace', placeholder='Text to replace...')
        self.replace_bak = []
        self.textbox = pn.widgets.input.TextAreaInput(
            name='Output CIF', 
            placeholder='Output CIF will be shown here...', 
            height=800
            )
        self.btn_replace = pn.widgets.Button(name='Replace RegEx', button_type='primary')
        self.btn_replace.on_click(self.on_click_replace)
        self.btn_undo = pn.widgets.Button(name='Undo replace', button_type='primary')
        self.btn_undo.on_click(self.on_click_undo)

        self.btn_parse = pn.widgets.Button(name='Parse CIF', button_type='primary')
        self.btn_parse.on_click(self.on_click_parse)

        from structure import structure_jsmol
        import bokeh.models as bmd
        self.jsmol_script_source = bmd.ColumnDataSource()
        self.applet = structure_jsmol(self.jsmol_script_source)

        space_groups_csv = Path(__file__).parent / "space_groups.csv"
        space_groups_df = pd.read_csv(space_groups_csv, index_col="_space_group_IT_number")
        self.space_groups_table = pn.widgets.DataFrame(space_groups_df, autosize_mode='fit_viewport')
        
    def servable(self):
        """Layout of the CIF section of the page."""
        self.column = pn.Column(
            pn.pane.HTML("""<h2>Copy and Paste CIF's info</h2>"""),
            self.name_input,
            self.cell_input,
            self.symm_input,
            self.coord_input,
            pn.Row(
                self.find,
                self.replace,
                pn.Column(
                    self.btn_replace,
                    self.btn_undo
                )
            ),
            self.btn_parse,
            pn.pane.Bokeh(self.applet),
            self.textbox,
            pn.pane.HTML("""<h2>Space Groups lookup table</h2>"""),
            self.space_groups_table,

            width=1000
        )
        return self.column.servable()

    def display(self, cif_str):
        """Update applet to show CIF."""
        from structure import structure_jsmol

        self.jsmol_script_source.data['script'] = [
"""load data "cifstring"
{}
end "cifstring"
""".format(str(cif_str))]
        
    def parse_cell_input(self):
        """Try first to understand a string like:
        'a = b = 37.2145Å, c = 4.0878 Å, α = β = 90° and γ = 120°'.
        If it fails, simply extract six floats.
        """
        fail_parsing = False

        data = self.cell_input.value
        data = re.sub("and", " ", data)  # remove "and" that makes conflicts with "a"
        data = re.sub("Ɣ", "γ", data)    # replace weird gamma
        data = re.sub("[^0-9.abcαβγ]", " ", data).split()
        if "." in data: data.remove(".") # remove isolate dots

        for i, val in enumerate(data):
            if val in 'abcαβγ':
                for j in data[i:]:
                    if j not in 'abcαβγ':
                        try:
                            self.cif_dict[val] = float(j)
                        except:
                            fail_parsing = True
                        break

        if fail_parsing or not all(celldim in self.cif_dict for celldim in 'abcαβγ'):
            data = self.cell_input.value
            data = re.sub("[^0-9.]", " ", data).split()
            if "." in data: data.remove(".")
            for i, celldim in enumerate('abcαβγ'):
                self.cif_dict[celldim] = float(data[i])

    def read_and_check_symm(self, symm_input):
        """Check if the input symmetry (_space_group_name_H-M_alt convention) starts with a correct character,
        and convert the string to upper/lower case to help ASE for its parsing.
        """
        first_char_list = {'A', 'C', 'F', 'I', 'P', 'R'}
        first_char_inp = symm_input.strip()[0].upper()
        other_char_inp = symm_input.strip()[1:].lower()
        if first_char_inp not in first_char_list:
            raise ValueError(f"No space group starts with '{first_char_inp}': check the table at the bottom!")
        return first_char_inp + other_char_inp

    def on_click_replace(self, event):
        text_initial = self.coord_input.value
        self.replace_bak.append(text_initial)
        text_replaced = re.sub(self.find.value,self.replace.value,text_initial)
        self.coord_input.value = text_replaced

    def on_click_undo(self, event):
        if len(self.replace_bak)==0:
            raise ValueError("No replaced text backup to load!")
        self.coord_input.value = self.replace_bak.pop()

    def on_click_parse(self, event):
        self.cif_dict = {} # Reset to avoid problems
        self.parse_cell_input() 

        self.cif_dict['symm'] = self.read_and_check_symm(self.symm_input.value)

        self.cif_dict['coord'] = []

        for line in self.coord_input.value.splitlines():
            ncols = len(line.split())
            if ncols==0 or ncols==1: # likely: \n or page number
                continue
            elif ncols==4: # likely: "atom_type x y z"
                self.cif_dict['coord'].append(line)
            elif ncols==5: # likely: "atom_type element x y z"
                d = line.split()
                newline = f'{d[0]} {d[2]} {d[3]} {d[4]}'
                self.cif_dict['coord'].append(newline)
            elif ncols==8: # likely: double column "atom1 x1 y1 z1 atom2 x2 y2 z2"
                d = line.split()
                newline1 = f'{d[0]} {d[1]} {d[2]} {d[3]}'
                newline2 = f'{d[4]} {d[5]} {d[6]} {d[7]}'
                self.cif_dict['coord'].append(newline1)
                self.cif_dict['coord'].append(newline2)
            else:
                raise ValueError(f"Impossible to parse line: '{line}'")

        filename = Path("./cifs/") / (self.name_input.value.strip() + ".cif")
        with open(filename, 'w') as ofile:
            print()

            print("data_crystal", file=ofile)
            print(" ", file=ofile)
            print("_cell_length_a    %.5f" % self.cif_dict['a'], file=ofile)
            print("_cell_length_b    %.5f" % self.cif_dict['b'], file=ofile)
            print("_cell_length_c    %.5f" % self.cif_dict['c'], file=ofile)
            print("_cell_angle_alpha %.5f" % self.cif_dict['α'], file=ofile)
            print("_cell_angle_beta  %.5f" % self.cif_dict['β'], file=ofile)
            print("_cell_angle_gamma %.5f" % self.cif_dict['γ'], file=ofile)
            print(" ", file=ofile)
            print(f"_symmetry_space_group_name_H-M  '{self.cif_dict['symm']}'", file=ofile)
            print(" ", file=ofile)
            print("loop_", file=ofile)
            print("_atom_site_label", file=ofile)
            #print("_atom_site_type_symbol", file=ofile)
            print("_atom_site_fract_x", file=ofile)
            print("_atom_site_fract_y", file=ofile)
            print("_atom_site_fract_z", file=ofile)
            for line in self.cif_dict['coord']:
                print(line, file=ofile)

        self.textbox.value = open(filename, 'r').read()

        print ('Printed CIF file:', filename)

        from ase.io import read, write
        from ase.io.cif import write_cif
        from ase.geometry.dimensionality import analyze_dimensionality
        from ase.build import make_supercell

        atoms = read(filename, format='cif') # need to load to unwrap?

        import tempfile
        with tempfile.TemporaryFile() as handle:
            write(handle, atoms, format='cif')
            handle.seek(0)
            self.cif_str = handle.read()

        self.display(self.cif_str.decode())

        

cif = CifParse()
cif.servable()
