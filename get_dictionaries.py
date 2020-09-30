#!usr/bin/env/ python

# First step: format Gemini panel information into gemini_dictionary containing {‘panel name’ : [‘gene symbols’]} for all panels in Gemini

import os

gemini_path = os.path.join('/home/Jay/projects/panel_matching/', 'gemini_panels_200522.txt')
with open(gemini_path) as gemini_file:
    gemini_panels = gemini_file.readlines()
    gemini_dictionary = {}
    for row in gemini_panels:
        entry = row.split('\t')
        gene_symbol = entry[2].strip()
        if entry[0] in gemini_dictionary.keys():
            gemini_dictionary[entry[0]].append(gene_symbol)
        else:
            gemini_dictionary[entry[0]] = [gene_symbol]

# Step 2: format PanelApp panel information into panelapp_dictionary containing {‘panel name’ : [‘gene symbols’]} for all panels in PanelApp
# Yu-Jin has provided us with a folder containing a text file for every panel.

import os

panelapp_dictionary = {}
panelapp_path = '/home/Jay/projects/panel_matching/200925_panelapp_dump'
for filename in os.listdir(panelapp_path):
    filepath = os.path.join(panelapp_path, filename)
    with open(filepath) as single_panel_object:
        single_panel = single_panel_object.readlines()
        lst_of_rows = []
        lst_of_rows = [row.split('\t') for row in single_panel]
        gene_symbols = []
        gene_symbols = [entry[-1].strip() for entry in lst_of_rows]
        panelapp_dictionary[filename[:-4]] = gene_symbols