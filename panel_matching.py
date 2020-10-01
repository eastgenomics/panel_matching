#!usr/bin/env/ python

# STEP 1: Format Gemini panel information into a gemini_dictionary containing {‘panel name’ : [‘gene symbols’]}, for all panels in Gemini
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
#print(gemini_dictionary.keys())

#------------------------------------------------------------------------------------------

# STEP 2: Format PanelApp panel information into a panelapp_dictionary containing {‘panel name’ : [‘gene symbols’]}, for all panels in PanelApp
# OPTION 2 (for when I have a better idea what on earth I'm doing) - access PanelApp panels and gene lists using the API.
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
#print(panelapp_dictionary.keys())

#------------------------------------------------------------------------------------------

#STEP 3: For each gemini panel, which panelapp panel (or combination thereof) best covers those genes?
# Yes, this section is a mess.

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

mapped_dictionary = {}
for gemini_panel, gemini_genes in gemini_dictionary.items():
    #Loop part 1: Initialise the output variables
    exact_matches = [] #panelapp panels which exactly match gemini panel
    bigger_panels = {} #panelapp panels which contain the gemini panel {'panel name':[list of genes in panel, number of surplus genes]}
    best_bigger_panel = [] #value from the bigger_panels entry with the smallest number of surplus genes
    subpanels = [] #panelapp panels which are subpanels of the gemini panel

    for panelapp_panel, panelapp_genes in panelapp_dictionary.items():
        #Sub-loop part 1: The easy cases - no overlap, exact overlap, or one list is contained within the other
        #S1a: If the panelapp panel doesn't contain any of the genes in the gemini panel, break the sub-loop
        missing_genes = []
        for gene in gemini_genes:
            if gene not in panelapp_genes:
                missing_genes.append(gene)
        if missing_genes == gemini_genes:
            continue
        
        #S1b: If the panelapp panel is identical to the gemini panel, add it to exact_matches and break the sub-loop
        elif panelapp_genes == gemini_genes:
            exact_matches.append(panelapp_panel)
            continue
        
        #S1c: If the panelapp panel contains all the genes in the gemini panel, add it to bigger_panels and break the sub-loop
        elif gemini_genes in panelapp_genes:
            bigger_panels[panelapp_panel] = [panelapp_genes, len(panelapp_genes - len(gemini_genes))
            continue
        
        #S1d: If the panelapp panel is a subpanel of the gemini panel, add it to subpanels (but DON'T break the sub-loop)
        elif panelapp_genes in gemini_genes:
            subpanels.append(panelapp_panel)

        #Sub-loop part 2: Working on solutions where the lists aren't identical and one doesn't contain the other
        #List the genes in (a) both panels (b) gemini panel only (c) panelapp panel only
        shared = []
        gem_only = []
        pan_only = []
        for gene in gemini_genes:
            if gene in panelapp_genes:
                shared.append(gene)
            else:
                gem_only.append(gene)
        for gene in panelapp_genes:
            if gene not in gemini_genes:
                pan_only.append(gene)

    #Loop part 2: 
    #If bigger_panels isn't empty, find the smallest of these panels. That's the best bigger panel.
    if len(bigger_panels.keys()) > 0:
        for panel, surplus_genes in bigger_panels.items():
            if len(best_bigger_panel) == 0:
                best_bigger_panel = [panel, len(surplus_genes)]
            elif len(surplus_genes) < best_bigger_panel[1]:
                best_bigger_panel = [panel, len(surplus_genes)]
    else:
        best_bigger_panel = ['N/A', 'N/A']

    #Loop part 3: Generate an output for the current gemini panel
    panel_answer = 'There are {match_count} PanelApp panels which are exact matches for this panel: {match_list}.'\
        'The shortest PanelApp panel which covers all the genes in this panel is {bigger_panel}, which also contains {bigger_surplus} other genes.'\
        '{subpanel_count} PanelApp panels are subsets of this panel: {subpanel_list}. A combination of these may cover all the required genes.'\
        .format(match_count=len(exact_matches), match_list=exact_matches, bigger=best_bigger_panel[0], bigger_surplus = best_bigger_panel[1], subpanel_count=len(subpanels), subpanel_list=subpanels)

    mapped_dictionary[gemini_panel] = panel_answer

print('To access the information for a particular Gemini panel, enter: mapped_dictionary[\'panel name\']')


# NOT PART OF THE PROGRAM, JUST FOR INFO--------------------
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
