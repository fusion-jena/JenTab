# This builds the chemical elements index as intersection between WD elements and DBP.
# We retrieve elements from WD including their symbol
# We look by the label at the dbr resources, we select the resource if it exactly found.


import pandas as pd
from os.path import realpath, join
import json


def build_index():
    # parse WD elements we retrieved during 2020
    query_taxon_file_path = join(realpath('.'), 'biodiv', 'WD_query_chemical_elements.csv')
    df = pd.read_csv(query_taxon_file_path)

    # parse DBpedia elements and transform that into label format
    query_dbp_chemical_elements_file_path = join(realpath('.'), 'biodiv', 'query_chemical_elements.csv')
    dbp_df = pd.read_csv(query_dbp_chemical_elements_file_path, names=['el'])
    dbp_ele = {}
    [dbp_ele.update({el.replace('http://dbpedia.org/resource/', '').replace('_', ' ').lower(): el}) for el in dbp_df['el'].to_list()]

    lbls = df['elLabel'].to_list()
    symbols = df['symbol'].to_list()

    abbr_dict = {}

    for symb, lbl in zip(symbols, lbls):
        if lbl in dbp_ele:
            abbr_dict[symb.lower()] = [{'labels': [lbl], 'uri': dbp_ele[lbl]}]

    # dump entries variable to json file
    print('dump entries to chemical_elements_mappings.json')
    with open(join(realpath('.'), 'biodiv', 'chemical_elements_mappings.json'), 'w', encoding='utf-8') as file:
        json.dump(abbr_dict, file)


def get_full_values(keywords):
    with open(join(realpath('.'), 'biodiv', 'chemical_elements_mappings.json'), 'r', encoding='utf-8') as file:
        lbls_dict = json.load(file)

    mapped = {}
    for k in keywords:
        mapped[k] = lbls_dict.get(k.lower(), [])
    return mapped


if __name__ == '__main__':
    # build_index()
    print(get_full_values(['C', 'Mn', 'Zn']))
