#!usr/bin/env/ python

#SECTION 1: Format Gemini panel information into a gemini_dictionary containing {‘panel name’ : [‘gene symbols’]}, for all panels in Gemini
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

#SECTION 2: Format PanelApp panel information into a panelapp_dictionary containing {‘panel name’ : [‘gene symbols’]}, for all panels in PanelApp
#OPTION 2 (for when I have a better idea what I'm doing) - access PanelApp panels and gene lists using the API.
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

#SECTION 3: For each gemini panel, which panelapp panel (or combination thereof) best covers those genes?
#What are the possible solutions?
#Single-panel solutions 
#	1. One panelapp panel which is exactly the same as the gemini panel (ideal solution)
#	2. The shortest panelapp panel which contains the gemini panel plus additional genes (may be a LOT additional genes)
#   3. The longest panelapp panel which is contained within the gemini panel (may be a LOT of missing genes, and may also have additional genes)
#Multi-panel solutions:
#   4. Multiple panelapp panels, which added together exactly replicate the gemini panel
#   5. Multiple panelapp panels, which added together cover all the relevant genes and some others (may be a LOT additional genes)
#   6. Multiple panelapp panels, which added together cover some of the relevant genes (may be a LOT of missing genes, and may also have additional genes)
#'Give up and go to the pub' case:
#   7. There are no panelapp panels which cover any genes in the gemini panel

def create_mapped_dict():
    mapped_dictionary = {} #takes form {'gemini panel name':'best panelapp match'}
    for gemini_panel, gemini_genes in gemini_dictionary.items():
        exact_matches = [] #panelapp panels which exactly match gemini panel
        bigger_panels = {} #panelapp panels which contain the gemini panel {'panel name':[list of genes in panel, number surplus genes]}
        shortest_bigger_panel = [] #value from the bigger_panels entry with the smallest number of surplus genes
        subpanels = [] #panelapp panels which are subpanels of the gemini panel

        for panelapp_panel, panelapp_genes in panelapp_dictionary.items():
            #A: The panelapp panel is identical to the gemini panel. Gets appended to exact_matches for that gemini panel.
            if panelapp_genes == gemini_genes:
                exact_matches.append(panelapp_panel)
                continue
        
            shared_genes = []
            gemini_only = []
            panelapp_only = []

            for gene in gemini_genes:
                if gene in panelapp_genes:
                    shared_genes.append(gene)
                elif gene not in panelapp_genes:
                    gemini_only.append(gene)
            for gene in panelapp_genes:
                if gene not in gemini_genes:
                    panelapp_only.append(gene)
        
            #B: The panelapp panel doesn't cover any genes in the gemini panel. Move to next panelapp panel.
            if gemini_only == gemini_genes:
                continue
        
            #C: The panelapp panel covers all the genes in the gemini panel, plus some others. Append panelapp panel name and number surplus genes to a dictionary for that gemini panel.
            elif gemini_genes in panelapp_genes:
                surplus = len(panelapp_genes) - len(gemini_genes)
                bigger_panels[panelapp_panel] = [panelapp_genes, surplus]
                continue
        
            #D: The panelapp panel is a subpanel of the gemini panel. DO SOMETHING TO COMBINE SUBSETS
            elif panelapp_genes in gemini_genes:
                subpanels.append(panelapp_panel)

        #MAIN LOOP: Generates an output for the current gemini panel
        #If there is an exact match, that's the best match.
        best_match = ''
        if exact_matches:
            best_match = 'PanelApp panels that exactly match this panel: {matches}.'.format(matches=exact_matches)

        #If there are any panels which cover all genes in the current gemini panel, the shortest of those is the best match
        elif bigger_panels:
            for panel, surplus in bigger_panels.items():
                if not shortest_bigger_panel:
                    shortest_bigger_panel = [panel, surplus]
                elif surplus < shortest_bigger_panel[1]:
                    shortest_bigger_panel = [panel, surplus]
            best_match = 'The PanelApp panel {panel} covers all of this panel\'s genes, plus {surplus} others.'.format(panel=shortest_bigger_panel[0], surplus = shortest_bigger_panel[1])

        #If there are any panels which are subpanels of the gemini panel:
        elif subpanels:
            best_match = 'PanelApp panels that are subsets of this panel: {subpanels}. A combination of these may cover all the required genes.'.format(subpanels=subpanels)

        #If there aren't any exact matches, panels which contain all the required genes, or subpanels...things get trickier.
        #find some way of ranking panels?????     

        mapped_dictionary[gemini_panel] = best_match
        #---END FUNCTION---

#create_gemini_dict()
#create_panelapp_dict()
#create_mapped_dict()

#Test: print all mapped_dictionary contents
#for key, value in mapped_dictionary.items():
    #if value:
        #print(key, value)

#Test: Search in terminal for match to specific panel
#search_item = input('Which Gemini panel are you interested in? ')
#print(mapped_dictionary[search_item])








# SECTION 4: NOT PART OF THE PROGRAM, JUST FOR INFO--------------------
# What sort of panel lengths are we dealing with?
gen_count = len(gemini_dictionary.keys())
gen_max = 0
gen_min = 600
gen_ave_sum = 0
for value in gemini_dictionary.values():
    gen_ave_sum += len(value)
    if len(value) == 0:
        continue
    elif len(value) > gen_max:
        gen_max = len(value)
    elif len(value) < gen_min:
        gen_min = len(value)
gen_ave = gen_ave_sum / gen_count
#print('There are {gen_count} Gemini panels. The biggest has {gen_max} genes, the smallest has {gen_min} genes, and the average size is {gen_ave}'.format(gen_count=gen_count, gen_max = gen_max, gen_min = gen_min, gen_ave = gen_ave))

pan_count = len(panelapp_dictionary.keys())
pan_max = 0
pan_min = 600
pan_ave_sum = 0
for value in panelapp_dictionary.values():
    pan_ave_sum += len(value)
    if len(value) == 0:
        continue
    elif len(value) > pan_max:
        pan_max = len(value)
    elif len(value) < pan_min:
        pan_min = len(value)
pan_ave = pan_ave_sum / pan_count
#print('There are {pan_count} PanelApp panels. The biggest has {pan_max} genes, the smallest has {pan_min} genes, and the average size is {pan_ave}'.format(pan_count=pan_count, pan_max = pan_max, pan_min = pan_min, pan_ave = pan_ave))
