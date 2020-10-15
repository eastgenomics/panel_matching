# panel_matching

The lab will be changing from gene panels designed in-house to more standardised panels described in PanelApp. The project aim is to find, for each in-house panel, the PanelApp panel which best represents it. 

Before we can begin comparing panels, we first need to manipulate data about the genes contained in each panel into a usable format. The sources of this information are 'gemini_panels_200522.txt', a .txt file containing tab-delimited information on the genes covered by each in-house panel; and '200925_panelapp_dump', a folder containing a similar .tsv file for each PanelApp panel.

The first two sections of code in the panel_matching.py file describe functions which produce a dictionary of panels and covered genes for both the in-house and PanelApp panels. The format of the resulting dictionaries is:

dictionary = {'panel 1 name':[list of genes in panel 1], ... , 'panel N name':[list of genes in panel N]}

In an ideal world, each in-house panel would be represented by a PanelApp panel which contains exactly the same genes. However, in practice this is not the case for the vast majority of panels. The objective is therefore how to identify the PanelApp panel which is least different to each in-house panel. When comparing two panels, there are two main ways in which they can differ:
1. Some genes in the in-house panel may not be present in the PanelApp panel (missing genes)
2. The PanelApp panel may contain additional genes which are not in the in-house panel (surplus genes)

In order to maximise the similarities between panels whilst minimising their differences, the approach taken here is to divide one by the other:
  Value for ranking = number of genes common to both panels / (missing genes + surplus genes)
 
This value is calculated for each PanelApp panel compared to each in-house panel. For each in-house panel, the five PanelApp panels with the highest values are then returned as output in a .csv file (mapping_output.csv) with their associated comparison values:
1. % coverage: proportion of genes in the in-house panel which are also in the PanelApp panel
2. % missing: proportion of genes in the in-house panel which are not in the PanelApp panel
3. % surplus: proportion of the PanelApp panel which is surplus, i.e. genes not in the in-house panel
4. ranked value: calculated as % coverage / (% missing + % surplus)

The case where 'missing genes' and 'surplus genes' are both equal to zero would normally result in a ZeroDivisionError when calculating the value for ranking. However, this actually indicates a case where the PanelApp panel is identical to the in-house panel, which is the optimal solution. A conditional statement has therefore been included to detect any instances of this case and set the ranking value to an arbitrarily high number, so that the relevant PanelApp panel is identified as the optimal match.

CONTROLS AND OUTPUT CHECK

Known exact matches act as good controls for checking output. Three in-house panels have corresponding PanelApp panels which are exact matches: 'CFTR single gene', 'Charge syndrome' and 'Ovarian Cancer_ICE'; which correspond to the PanelApp panels 'Additional findings reproductive carrier status_0.5', 'CHARGE syndrome_0.11' and 'Inherited ovarian cancer (without breast cancer)_2.2'.

Some in-house panels are used more frequently than others, and so accurate matching is potentially more important for these. The second tab of the 'output_final.xlsx' file shows the matches generated for the 10 most frequently used in-house panels. For each of these, matching identifies a PanelApp panel whose name reflects that of the in-house panel, and which for the most part appears to represent the panel's genes well. The matching for Epileptic Encephalopathy panels 1 and 2, where the matched panels cover practically all the in-house genes but with a large surplus, may indicate unavoidable differences in the panels used for a specific phenotype.

LIMITATIONS

There are some in-house panels, particularly very short panels of only a few genes, where the solution is less than ideal. For example, the in-house panel for Aarskog-Scott syndrome only contains one gene, which is FGD1. There are 10 PanelApp panels which cover FGD1, but the shortest of these (IUGR and IGF abnormalities_1.30) is 95 genes long. Whilst the matching algorithm is able to identify the best match, it cannot recitfy the underlying problem that there is no good match for this panel.
