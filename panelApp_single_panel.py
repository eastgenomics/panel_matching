#!usr/bin/env/ python

with open('Familial hypercholesterolaemia.tsv') as whole_file:
    lst_of_rows = []
    lst_of_rows = [row for row in whole_file]
    del lst_of_rows[0]

    gene_symbols = []
    gene_symbols = [entry.split('\t')[2] for entry in lst_of_rows]

print(gene_symbols)