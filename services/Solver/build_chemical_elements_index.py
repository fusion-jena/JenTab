# SELECT ?el ?elLabel ?symbol
# WHERE {
#   ?el wdt:P31 wd:Q11344 .
#   ?el wdt:P246 ?symbol
#   SERVICE wikibase:label {bd:serviceParam wikibase:language "en".}
#   }

import pandas as pd
from os.path import realpath, join
import json


def build_index():
    query_taxon_file_path = join(realpath('.'), 'biodiv', 'query_chemical_elements.csv')
    df = pd.read_csv(query_taxon_file_path)

    # retrieve actual species Qxxx
    elems = df['el'].to_list()
    # substitute full url with only QIds
    elems = [i.replace('http://www.wikidata.org/entity/', '') for i in elems]

    lbls = df['elLabel'].to_list()
    symbols = df['symbol'].to_list()

    abbr_dict = {}

    for symb, lbl, elem in zip(symbols, lbls, elems):
        abbr_dict[symb.lower()] = [{'labels': [lbl], 'uri': elem}]

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


# def investigate_keys():
#     # from this method we knew that all chemical_elements has maximumn length of 3
#     with open(join(realpath('.'), 'biodiv', 'chemical_elements_mappings.json'), 'r', encoding='utf-8') as file:
#         abbr_dict = json.load(file)
#     print(len(abbr_dict.keys()))
#     max = 0
#     min = 1000
#     for key in abbr_dict.keys():
#         if len(key) > max:
#             max = len(key)
#         if len(key) < min:
#             min = len(key)
#     print(max)
#     print(min)

if __name__ == '__main__':
    build_index()
    # investigate_keys()
    print(get_full_values(['C', 'Mn']))
