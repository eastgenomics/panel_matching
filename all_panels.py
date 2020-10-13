#!usr/bin/env/ python

#SECTION 1: Format Gemini panel information into a gemini_dictionary containing {‘panel name’ : [‘gene symbols’]}, for all Gemini panels
def create_gemini_dict():
    import os
    gemini_path = os.path.join('c:/users/Jay/documents/projects/panel_matching/', 'gemini_panels_200522.txt') #On PC
    #gemini_path = os.path.join('/home/Jay/projects/panel_matching/', 'gemini_panels_200522.txt') #On laptop
    with open(gemini_path) as gemini_file:
        gemini_panels = gemini_file.readlines()
        gemini_dictionary = {}
        for row in gemini_panels:
            if row[0:4] == 'GEL_':
                continue
            entry = row.split('\t')
            gene_symbol = entry[2].strip()
            if (entry[0] in gemini_dictionary.keys()) and (gene_symbol not in gemini_dictionary[entry[0]]) and (gene_symbol != ''):
                gemini_dictionary[entry[0]].append(gene_symbol)
            elif gene_symbol != '':
                gemini_dictionary[entry[0]] = [gene_symbol]
    return gemini_dictionary

#SECTION 2: Format PanelApp panel information into a panelapp_dictionary containing {‘panel name’ : [‘gene symbols’]}, for all PanelApp panels
def create_panelapp_dict():
    import os
    panelapp_dictionary = {}
    panelapp_path = 'c:/Users/Jay/Documents/Projects/panel_matching/200925_panelapp_dump' #On PC
    #panelapp_path = '/home/Jay/projects/panel_matching/200925_panelapp_dump' #On laptop
    for filename in os.listdir(panelapp_path):
        filepath = os.path.join(panelapp_path, filename)
        with open(filepath) as single_panel_object:
            single_panel = single_panel_object.readlines()
            lst_of_rows = []
            lst_of_rows = [row.split('\t') for row in single_panel]
            gene_symbols = []
            for row in lst_of_rows:
                if (row[-1] != '') and (row[-1].strip() not in gene_symbols):
                    gene_symbols.append(row[-1].strip())
            panelapp_dictionary[filename[:-4]] = gene_symbols
    return panelapp_dictionary

#Outputs excel file showing genes in each panel

gemini_dictionary = create_gemini_dict()
panelapp_dictionary = create_panelapp_dict()

import csv
with open('all_panels.csv','w', newline = '') as file_object:
    all_panels = []
    all_panels.append(['GEMINI PANELS'])
    for panel, genes in gemini_dictionary.items():
        all_panels.append([panel])
        row = [gene for gene in genes]
        all_panels.append(row)
        all_panels.append('\n')

    all_panels.append('\n')
    all_panels.append(['PANELAPP PANELS'])
    for panel, genes in panelapp_dictionary.items():
        all_panels.append([panel])
        row = [gene for gene in genes]
        all_panels.append(row)
        all_panels.append('\n')

    output = csv.writer(file_object)
    for entry in all_panels:
        output.writerow(entry)