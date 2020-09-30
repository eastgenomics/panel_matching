#!usr/bin/env/ python

# Step 1: format Gemini panel information into gemini_dictionary containing {‘panel name’ : [‘gene symbols’]} for all panels in Gemini

import os

gemini_path = os.path.join('/home/Jay/projects/panel_matching/', 'gemini_panels_200522.txt')
with open(gemini_path) as gemini_file:
    gemini_panels = gemini_file.readlines()
    gemini_dictionary = {}
    for row in gemini_panels:
        if row[0:4] == 'GEL_':
            continue
        entry = row.split('\t')
        gene_symbol = entry[2].strip()
        if entry[0] in gemini_dictionary.keys() and gene_symbol != '':
            gemini_dictionary[entry[0]].append(gene_symbol)
        elif gene_symbol != '':
            gemini_dictionary[entry[0]] = [gene_symbol]


# Step 2: format PanelApp panel information into panelapp_dictionary containing {‘panel name’ : [‘gene symbols’]} for all panels in PanelApp
# Yu-Jin has provided us with a folder containing a text file for every panel.

panelapp_dictionary = {}
panelapp_path = '/home/Jay/projects/panel_matching/200925_panelapp_dump'
for filename in os.listdir(panelapp_path):
    filepath = os.path.join(panelapp_path, filename)
    with open(filepath) as single_panel_object:
        single_panel = single_panel_object.readlines()
        lst_of_rows = []
        lst_of_rows = [row.split('\t') for row in single_panel]
        gene_symbols = []
        gene_symbols = [entry[-1].strip() for entry in lst_of_rows if entry[-1].strip() != '']
        panelapp_dictionary[filename[:-4]] = gene_symbols


# Step 3: Once we have the two dictionaries, we need to find the closest match when mapping PanelApp panels onto Gemini panels
# First consideration: How do we want to return the results?
#   mapped_dictionary = {'gemini panel' : [list of panelapp panels]}

# Second consideration: What are the possible outcomes when trying to map to a single Gemini panel?
#In order of how good a solution it is: 
#	1. There is a panelapp panel which is exactly the same as the gemini panel
#	2. A few panelapp panels together exactly replicate the gemini panel
#The closest match covers all the genes, plus some others:
#	3. A single panelapp panel covers all the genes, plus a few others
#	4. A combination of panelapp panels together cover all the genes, plus a few others
#The closest match doesn't cover all the genes:
#	5. A single panelapp panel covers some of the genes	
#	6. A combination of panelapp panels together cover some of the genes
#Problematic cases:
#	7. A single panelapp panel covers all the genes, but a LOT of others
#	8. The genes can be covered by a combination of a LOT of panelapp panels
#Give-up-and-go-to-the-pub case:
#   9. There are no panelapp panels which have any genes in common with the gemini panel

mapped_dictionary = {}
for gemini_panel, gemini_genes in gemini_dictionary.items():
    for panelapp_panel, panelapp_genes in panelapp_dictionary.items():
            closest_map = []