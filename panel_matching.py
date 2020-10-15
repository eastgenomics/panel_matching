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
            if row[0:4] == 'GEL_': #omit GEL panels
                continue
            entry = row.split('\t')
            gene_symbol = entry[2].strip()
            if gene_symbol: #omit rows without a gene symbol
                if entry[0] not in gemini_dictionary.keys(): #if the row's panel isn't already in the dictionary, create one with the row's gene
                    gemini_dictionary[entry[0]] = [gene_symbol]
                elif (entry[0] in gemini_dictionary.keys()) and (gene_symbol not in gemini_dictionary[entry[0]]): #if the row's panel is in the dictionary but doesn't contain the row's gene, append the gene to the panel
                    gemini_dictionary[entry[0]].append(gene_symbol)
                gemini_dictionary[entry[0]].sort() #sort the genes in each panel alphabetically
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
            panelapp_dictionary[filename[:-4]] = sorted(gene_symbols)
    return panelapp_dictionary

#SECTION 3: For each Gemini panel, which PanelApp panel best covers those genes?
def create_mapped_dict():
    import csv
    import operator
    gemini_dictionary = create_gemini_dict()
    panelapp_dictionary = create_panelapp_dict()
    mapped_dictionary = {}
    for gemini_panel, gemini_genes in gemini_dictionary.items():
        ratio_list = []
        for panelapp_panel, panelapp_genes in panelapp_dictionary.items():
            #Identify differences between gemini and panelapp panels
            shared_genes = set(gemini_genes).intersection(set(panelapp_genes))
            shared_count = len(shared_genes)
            panelapp_only = len(panelapp_genes) - shared_count
            gemini_only = len(gemini_genes) - shared_count
        
            #If the panelapp panel doesn't cover any genes in gemini panel, skip to the next panelapp panel
            if not shared_genes:
                continue

            #Calculate value for ranking:
            pc_coverage = shared_count / len(gemini_genes)  #proportion of genes in gemini panel covered by panelapp panel - ideally high
            pc_missing = gemini_only / len(gemini_genes)    #proportion of genes in gemini panel not covered by panelapp panel - ideally low
            pc_surplus = panelapp_only / len(panelapp_genes)  #proportion of panelapp panel which is surplus - ideally low

            if pc_surplus == 0 and pc_missing == 0: #optimal case where a panelapp panel exactly matches the gemini panel
                rank_value = 50
                ratio_list.append([panelapp_panel, pc_coverage, pc_missing, pc_surplus, rank_value])
            else:
                rank_value = pc_coverage / (pc_surplus + pc_missing)
                ratio_list.append([panelapp_panel, pc_coverage, pc_missing, pc_surplus, rank_value])

        #Output is the 5 panelapp panels with the highest rank values for this gemini panel
        sort_by_ratio = sorted(ratio_list, key=operator.itemgetter(-1), reverse = True)
        top_five = sort_by_ratio[:5]
        mapped_dictionary[gemini_panel] = top_five
    
    #Create a csv file showing top 5 panelapp panels for each gemini panel
    with open('mapping_output.csv','w', newline = '') as file_object:
        mapping_output = []
        for key, value in mapped_dictionary.items():
            mapping_output.append([key, gemini_dictionary[key]])
            mapping_output.append(['PanelApp panel','% Coverage', '%Missing', '% Surplus','Ranked Value'])
            for panel in value:
                row = (panel[0], panel[1], panel[2], panel[3], panel[4], panelapp_dictionary[panel[0]])
                mapping_output.append(row)
            mapping_output.append('\n')
        output = csv.writer(file_object)
        for entry in mapping_output:
            output.writerow(entry)

    return mapped_dictionary

create_mapped_dict()
