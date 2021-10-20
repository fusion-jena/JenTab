import pandas as pd
from os.path import realpath, join
from external_services.wikidata_proxy_service import Wikidata_Proxy_Service
from config import LABELS_FOR_BATCH_SIZE
import json


def get_batch(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i + n]


def get_label_for_taxons():
    # Query file is built via this SPARQL query
    # SELECT DISTINCT *
    # WHERE {
    #   ?species wdt:P31 wd:Q16521
    #   }
    # load query_taxons results
    query_taxon_file_path = join(realpath('.'), 'biodiv', 'query_taxons.csv')
    df = pd.read_csv(query_taxon_file_path)

    # retrieve actual species Qxxx
    instances = df['species'].to_list()

    # substitute full url with only QIds
    instances = [i.replace('http://www.wikidata.org/entity/', '') for i in instances]

    # Conditional init of endpoint service.
    proxyService = Wikidata_Proxy_Service()

    # temp for current batch entries
    entries = {}

    # batch number to be printed
    i = 0
    # process given instances in a batch mode
    for batch_q in get_batch(instances, LABELS_FOR_BATCH_SIZE):
        print('batch {} getting labels ...'.format(i))

        # get labels for the current batch
        labels = proxyService.get_labels_for_lst.send([batch_q, "en"])

        # obtain 2 words labels only
        [[entries.update({el['l']: qi}) for el in labels[qi] if len(el['l'].split(' ')) == 2] for qi in batch_q]

        # next batch number
        i += 1

    print('dump entries to taxon_labels.json')
    # dump entries variable to json file
    with open(join(realpath('.'), 'biodiv', 'taxon_full_lbl_mappings.json'), 'w', encoding='utf-8') as file:
        json.dump(entries, file)

    print('No. 2 words labels is: {}'.format(len(entries)))


def updat_dict(lbl_dict, abbr_lbl, lbl, Qxx):
    if abbr_lbl not in lbl_dict.keys():
        # create candidate format expected by Solver
        lbl_dict.update({abbr_lbl: [{'labels': [lbl], 'uri': Qxx}]})
    else:
        if Qxx not in lbl_dict[abbr_lbl]:
            lbl_dict[abbr_lbl].append({'labels': [lbl], 'uri': Qxx})


def build_index():
    # load taxon_labels json file
    with open(join(realpath('.'), 'biodiv', 'taxon_full_lbl_mappings.json'), 'r', encoding='utf-8') as file:
        labels = json.load(file)

    lbl_dict = {}

    for l, Q in labels.items():
        parts = l.split(' ')
        key = parts[0][0] + '.' + parts[1]
        # apply actual process (abbreviate first word) using one letter
        updat_dict(lbl_dict, key, l, Q)
        # apply actual process (abbreviate first word) using two letters
        key = parts[0][0:2] + '.' + parts[1]
        updat_dict(lbl_dict, key, l, Q)

    # json dump
    with open(join(realpath('.'), 'biodiv', 'taxon_abbrv_lbl_mappings.json'), 'w', encoding='utf-8') as file:
        json.dump(lbl_dict, file)

    print('No. stored keys in the dictionary is: {}'.format(len(lbl_dict.keys())))


def get_full_values(keywords):
    with open(join(realpath('.'), 'biodiv', 'taxon_abbrv_lbl_mappings.json'), 'r', encoding='utf-8') as file:
        lbls_dict = json.load(file)

    mapped = {}
    for k in keywords:
        mapped[k] = lbls_dict.get(k, [])
    return mapped


import json
# in action
if __name__ == '__main__':
    # get_label_for_taxons()
    # build_index()
    # res = get_full_values(['C.glauca', 'L.glaber', 'L.formosana', 'C.sclerophylla', 'D.glaucifolia'])
    res = get_full_values(['C.glauca'])
    lst =['wd:'+item['uri'] for item in res['C.glauca']]
    print(lst)

