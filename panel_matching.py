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
            if entry[0] in gemini_dictionary.keys() and gene_symbol != '':
                gemini_dictionary[entry[0]].append(gene_symbol)
            elif gene_symbol != '':
                gemini_dictionary[entry[0]] = [gene_symbol]
    return gemini_dictionary

#SECTION 2: Format PanelApp panel information into a panelapp_dictionary containing {‘panel name’ : [‘gene symbols’]}, for all PanelApp panels
#Option for when I have a better idea what I'm doing - access PanelApp panels and gene lists using the API
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
            gene_symbols = [entry[-1].strip() for entry in lst_of_rows if entry[-1].strip() != '']
            panelapp_dictionary[filename[:-4]] = gene_symbols
    return panelapp_dictionary

#SECTION 3: For each Gemini panel, which PanelApp panel best covers those genes?
#The ideal solution is that a PanelApp panel exactly matches the Gemini panel. Unfortunately, this is only true for 3 Gemini panels.

#The approach taken here is to determine, for each Gemini panel and each PanelApp panel:
#   (a) the % genes in the Gemini panel which the PanelApp panel covers (ideally high)
#   (b) the % genes in the PanelApp panel which are not in the Gemini panel (surplus genes, ideally low)

#The script performs 2 rankings. Firstly, panels are split into ranks to select for decreasingly high values of (a). Secondly, each rank is ordered by values of (b).
#The best match is the panel from the highest rank with the lowest value for (b).

def create_mapped_dict():
    import csv
    gemini_dictionary = create_gemini_dict()
    panelapp_dictionary = create_panelapp_dict()
    
    mapped_dictionary = {}
    for gemini_panel, gemini_genes in gemini_dictionary.items():
        best_match = ''
        rank_values = {}

        for panelapp_panel, panelapp_genes in panelapp_dictionary.items():
            #If the panelapp panel is identical to gemini panel (best-case scenario), save as best match and break out of sub-loop
            if panelapp_genes == gemini_genes:
                best_match = panelapp_panel
                break
        
            #Identify differences between gemini and panelapp panels
            shared_genes = 0
            panelapp_only = 0
            gemini_only = 0
            gemini_only_genes = []

            for gene in gemini_genes:
                if gene in panelapp_genes:
                    shared_genes += 1
                elif gene not in panelapp_genes:
                    gemini_only += 1
                    gemini_only_genes.append(gene)
            for gene in panelapp_genes:
                if gene not in gemini_genes:
                    panelapp_only += 1
        
            #If the panelapp panel doesn't cover any genes in gemini panel, skip to the next panelapp panel
            if gemini_only_genes == gemini_genes:
                continue

            #D: Calculate values for ranking
            pc_coverage = shared_genes / gemini_genes #percentage of gemini genes covered by this panel
            pc_surplus = panelapp_only / panelapp_genes #surplus genes (those not in gemini panel) as a percentage of panelapp panel length
            rank_values[panelapp_panel] = [pc_coverage, pc_surplus]
        
        #If a panel was an exact match, that's the best match.
        if best_match:
            mapped_dictionary[gemini_panel] = best_match
            continue

        #Otherwise, panels are ranked for the highest % gemini genes covered AND the fewest surplus.
        else:
            list_of_ranks = {}
            for i in range(6):
                list_of_ranks[i] = []
                if i == 1:
                    for panel, values in rank_values.items():
                        if values[0] == 1 and 0 <= values[1] <= 0.5: #Rank 1 - panels which cover 100% of gemini genes and contain <=50% surplus genes
                            if not list_of_ranks[1]:
                                list_of_ranks[1] = [panel, values[1]]
                            elif values[1] < list_of_ranks[1][1]:
                                list_of_ranks[1] = [panel, values[1]]
                else:
                    for panel, values in rank_values.items():
                        if (1-(0.1 * (i-1))) <= values[0] < (1-(0.1 * (i-2))) and 0 <= values[1] <= 0.5: #Ranks 2-6 - bounds of (% gemini genes covered) decrease by 10% with each rank
                            if not list_of_ranks[i]:
                                list_of_ranks[i] = [panel, values[1]]
                            elif values[1] < list_of_ranks[i][1]:
                                list_of_ranks[i] = [panel, values[1]]                    
           
                if list_of_ranks[i]: #break the ranking loop at the highest occupied rank (most gemini genes covered with <=50% surplus genes)
                    best_match = list_of_ranks[i][0]
                    mapped_dictionary[gemini_panel] = best_match
    
    #Create a csv file showing the mapping of panelapp to gemini panels
    with open('mapping_output.csv','w') as file_object:
        mapping_output = []
        for key, value in mapped_dictionary.items():
            row = {'Gemini panel':key, 'Gemini panel genes':gemini_dictionary[key], 'PanelApp panel':value, 'PanelApp panel genes':panelapp_dictionary[value]}
            mapping_output.append(row)
        fields = ['Gemini panel', 'Gemini panel genes', 'PanelApp panel', 'PanelApp panel genes']
        output = csv.DictWriter(file_object, fieldnames = fields)
        output.writeheader()
        for entry in mapping_output:
            output.writerow(entry)
    
    return mapped_dictionary

create_mapped_dict()
