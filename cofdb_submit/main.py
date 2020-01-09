#!/usr/bin/env python
import panel as pn


# In[16]:


"""Check consistency of curated COF database"""
import pandas
import datetime
import os
CURATED_COFS=os.environ.get('CURATED_COFS', os.path.abspath('./CURATED-COFs'))
PAPER_FILE = os.path.join(CURATED_COFS, 'cof-papers.csv')
FRAMEWORKS_FILE = os.path.join(CURATED_COFS, 'cof-frameworks.csv')
CIFS_FOLDER = os.path.join(CURATED_COFS, 'cifs')

def parse_cofs_id(id):
    return {
        'year': id[1:3],
        'counter': int(id[3:5]),
    }

def mint_paper_id():
    
    df_papers = pandas.read_csv(PAPER_FILE)
    last_id = sorted(df_papers['CURATED-COFs paper ID'])[-1]
    year = str(datetime.datetime.now().year)
    
    last_dict = parse_cofs_id(last_id)
    
    #import pdb; pdb.set_trace()
    if last_dict['year'] == year[2:]:
        counter = last_dict['counter'] + 1
    else:
        counter = 0
        
    return "p{:s}{:02d}".format(year[2:], counter)

def mint_cof_id(paper_id, charge, dimensionality):
    df_frameworks = pandas.read_csv(FRAMEWORKS_FILE)
    other_cofs = [ id for id in df_frameworks["CURATED-COFs ID"] if id.startswith(paper_id[1:])]
    counter = len(other_cofs)
    
    return "{paper}{counter}{charge}{dim}".format(paper=paper_id[1:], counter=str(counter), charge=charge,
                                                  dim=dimensionality)
 
        


# In[ ]:


"""Add paper info"""
"CURATED-COFs paper ID","Reference","URL","Title"
"p0500","Science, 2005, 310, 1166-1170","http://science.sciencemag.org/content/310/5751/1166.short","Porous, crystalline, covalent organic frameworks"

pn.extension()

inp_doi = pn.widgets.TextInput(name='Publication DOI', placeholder="10.1021/jacs.9b01891")
btn_doi = pn.widgets.Button(name='Fetch metadata', button_type='primary')

inp_reference = pn.widgets.TextInput(name='Publication reference', placeholder='')
inp_title = pn.widgets.TextInput(name='Publication title', placeholder='')
inp_year = pn.widgets.TextInput(name='Publication year', placeholder='')
inp_paper_id = pn.widgets.TextInput(name='CURATED-COFs paper ID', placeholder='')
inp_url = pn.widgets.TextInput(name='Publication URL', placeholder='')

div_out = pn.widgets.StaticText(name='Output', value='')
btn_add_paper = pn.widgets.Button(name='Add paper', button_type='primary')

def get_metadata(doi):
    import requests
    import json
    response = requests.get(url="http://dx.doi.org/"+doi, 
            headers={"accept":"application/rdf+xml;q=0.5, application/vnd.citationstyles.csl+json;q=10"})
    return json.loads(response.content)

def on_click_fetch(event):
    import dateutil
    from crossref.restful import Works
    
    # test data
    inp_doi.value = inp_doi.value or "10.1021/jacs.9b01891"
    
    works = Works()
    print("Querying Crossref API for doi {}".format(inp_doi.value))
    metadata = works.doi(inp_doi.value)
    inp_title.value = str(metadata['title'][0])
    
    year = str(dateutil.parser.parse(metadata['indexed']['date-time']).year)
    inp_year.value = year
    
    journal = str(metadata['container-title'][0])
    inp_reference.value = "{}, {}, {}, {}".format(journal, year, metadata['volume'], metadata['page'])
    
    inp_url.value = "https://doi.org/" + inp_doi.value
    
    inp_paper_id.value = mint_paper_id()
        
btn_doi.on_click(on_click_fetch)


def on_click_add(event):
    """Add paper to list"""
    if not (inp_paper_id.value and inp_reference.value and inp_url.value and inp_title.value):
        btn_add_paper.button_type = 'danger'
        return
    
    btn_add_paper.button_type = 'primary'
        
    line = '"{id}","{ref}","{url}","{title}"\n'.format(id=inp_paper_id.value, ref=inp_reference.value, 
                                                  url=inp_url.value, title=inp_title.value)
    print(line)
    with open(PAPER_FILE, 'a+') as handle:
        handle.write(line)
            
    btn_add_paper.button_type = 'success'
        
btn_add_paper.on_click(on_click_add)

column = pn.Column(
    pn.pane.HTML("""<h2>Add Paper</h2>"""),
    pn.Row(inp_doi, btn_doi),
    inp_title,
    inp_year,
    inp_reference,
    inp_url,
    inp_paper_id,
    btn_add_paper,
)

column.servable()

# # gspec = pn.GridSpec(sizing_mode='stretch_both', max_width=900)
# # gspec[0, 0] = explorer.structure
# # gspec[1, 0] = explorer.ener_plot
# # gspec[2, 0] = explorer.iso_plot
# # gspec.servable()

# tabs = pn.Tabs()
# tabs.extend([
#     ("Metadata", explorer.metadata),
# #   ('Reported structure', explorer.structure_ref),
# #     ('DFT-optimization energy', explorer.ener_plot),
# #     ('DFT-optimized structure', explorer.structure_opt),
# #     ('Isotherms', explorer.iso_plot),
# #     ('CCS process', explorer.process),
# ])

# pn.extension()
# tabs.servable()


# In[ ]:


"""Add CIF info"""
"CURATED-COFs ID","Source","Name","Elements","Duplicate found","Modifications"
"05000N2","tong-v2, 035","COF-1","H,B,C,O","Science, 2005, 310, 1166-1170","none","none"

class CifForm():
    """Input form for CIF file"""
    
    def __init__(self):
        
        # Tested this with panel 0.7.0a14, but loading the app was very slow
        # inp_cif = pn.widgets.input.TextAreaInput(name='CIF', value="""
        # data_crystal
        #  
        # _cell_length_a    
        # _cell_length_b    
        # _cell_length_c    
        # _cell_angle_alpha
        # _cell_angle_beta  
        # _cell_angle_gamma 
        # 
        # _symmetry_space_group_name_H-M  'P 1'
        #  
        # loop_
        # _atom_site_label
        # _atom_site_fract_x
        # _atom_site_fract_y
        # _atom_site_fract_z
        # """)
        self.inp_cif = pn.widgets.FileInput(name='CIF')  
        self.btn_cif = pn.widgets.Button(name='Parse CIF', button_type='primary')
        self.btn_cif.on_click(self.on_click_parse)
        
        from cofdb_submit.structure import structure_jsmol
        import bokeh.models as bmd
        self.jsmol_script_source = bmd.ColumnDataSource()
        self.applet = structure_jsmol(self.jsmol_script_source)

        self.inp_source = pn.widgets.Select(name='CIF source', options={ 'Supporting information': 'SI', 'CSD': 'CSD', 'Tong database': 'tong-v2' })
        self.inp_name = pn.widgets.TextInput(name='CIF name', placeholder='As used in publication')
        self.inp_dimensionality = pn.widgets.Select(name='CIF dimensionality', options={ '2D': '2D', '3D': '3D' })
        self.inp_elements = pn.widgets.TextInput(name='CIF elements', placeholder='C,H,...')
        self.inp_duplicate = pn.widgets.TextInput(name='CIF duplicate found', value='none')
        self.inp_modifications = pn.widgets.TextInput(name='CIF modifications', placeholder='xy alignment, replicated along z, ...')
        self.inp_charge = pn.widgets.Select(name='CIF charge', options={ 'Neutral': 'N', 'Charged': 'C' })
        self.inp_cof_id = pn.widgets.TextInput(name='COF ID', value='none')
        self.btn_mint_id = pn.widgets.Button(name='Mint', button_type='primary')
        self.btn_mint_id.on_click(self.mint_framework_id)
           
        self.btn_add_cif = pn.widgets.Button(name='Add CIF', button_type='primary')
        self.btn_add_cif.on_click(self.on_click_add)
        
    @property
    def info_dict(self):
        return {
            'cof_id': self.inp_cof_id.value,
            'source': self.inp_source.value,
            'name': self.inp_name.value,
            'dimensionality': self.inp_dimensionality.value,
            'elements': self.inp_elements.value,
            'duplicate': self.inp_duplicate.value,
            'modifications': self.inp_modifications.value,
            'charge': self.inp_charge.value,
        }
    
    def servable(self):
        self.column = pn.Column(
            pn.pane.HTML("""<h2>Add CIF</h2>"""),
            pn.Row(self.inp_cif, self.btn_cif),
            pn.pane.Bokeh(self.applet),
            self.inp_source, 
            self.inp_name,  
            self.inp_dimensionality, 
            self.inp_elements,
            self.inp_duplicate,
            self.inp_modifications,
            self.inp_charge,
            pn.Row(self.inp_cof_id, self.btn_mint_id),
            self.btn_add_cif,
        )
        return self.column.servable()
        
    def on_click_parse(self, event):
        from ase.io import read, write
        from ase.io.cif import write_cif
        from ase.geometry.dimensionality import analyze_dimensionality
        from ase.build import make_supercell
        from io import StringIO, BytesIO
        import re
        
        cif_str = self.inp_cif.value.decode()
        atoms = read(StringIO(cif_str), format='cif')
        
        formula = atoms.get_chemical_formula()
        elements = [e for e in re.split(r'\d+', formula) if e]
        self.inp_elements.value = ",".join(elements)
        
        intervals = analyze_dimensionality(atoms, method='RDA')
        if intervals[0].dimtype == '2D' or True:
            self.inp_dimensionality.value = '2D'
            
            # multiply cell if cell vectors are too short
            cell_lengths = atoms.get_cell_lengths_and_angles()[0:3]
            if any(cell_lengths < 4.5):
                import numpy as np
                p = np.diag([2 if l < 4.5 else 1 for l in cell_lengths  ])
                atoms = make_supercell(atoms, p)
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
        """Add framework to list and add CIF file."""
        from ase.io import write
        info = self.info_dict
        if not all(v for k,v in info.items() if k not in ['modifications']):
            self.btn_add_cif.button_type = 'danger'
            return
        
        self.btn_add_cif.button_type = 'primary'    
        line = '"{id}","{source}","{name}","{elements}","{duplicates}","{mod}"\n'          .format(id=info['cof_id'], source=info['source'], name=info['name'], elements = info['elements'],
                 duplicates=info['duplicate'], mod=info['modifications'])
        print(line)
        with open(FRAMEWORKS_FILE, 'a+') as handle:
           handle.write(line)
            
        cif_path = os.path.join(CIFS_FOLDER, info['cof_id'] + '.cif')
            
        print("Writing {}".format(cif_path))
        write(cif_path, self.atoms)
        #with open(cif_path, 'wb') as handle:
        #    handle.write(self.inp_cif.value)
            
        self.btn_add_cif.button_type = 'success'
            
    def mint_framework_id(self, event):
        self.inp_cof_id.value = mint_cof_id(inp_paper_id.value, self.inp_charge.value, self.inp_dimensionality.value[0])
        
    def display(self, cif_str):
        """Update applet to show CIF."""
        from cofdb_submit.structure import structure_jsmol
        
        self.jsmol_script_source.data['script'] = [
"""load data "cifstring"
{}
end "cifstring"
""".format(str(cif_str))]
        #print(self.jsmol_script_source.data['script'])
        

cif = CifForm()
cif.servable()

