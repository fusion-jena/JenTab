from os.path import realpath, join
import edlib
from functools import partial
from utils import util_log, util
from config import *
import numpy as np
from ftfy import fix_text
from config import ASSET_PATH


def load_file(file_object, chunk_size=chunk_size, lazy=True):
    """
    Lazy function (generator) to read a file chunk  by chunk
    :param file_object: file
    :param chunk_size: Default chunk size: 200MB.
    :return:
    """
    if not lazy:
        yield file_object.read()
    else:
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data


def get_dist(words, labels):
    """
    :param words: Wikidata label
    :param label: cell value
    :return: levenshtein dist between word and given label
    """
    res = []

    for word in words:
        dists = [edlib.align(label, word)['editDistance'] for label in labels]
        dist_arr = np.asarray(dists, dtype=np.float32)
        idx = dist_arr.argsort()
        res.append((dists[idx[0]], word, labels[idx[0]]))

    return res


def get_nearest_candidate(chunk, values):
    """
    :param chunk: part of the labels file
    :param values: cell values
    :return: candidate label with minimum levenshtein distance
    """

    # list of labels
    labels = [l for l in chunk.split('\n')]  # filter on real strings only

    # init threads pool
    pool = multiprocessing.Pool(processes=cpus)

    # delegate with two params the given cell value and labels
    func = partial(get_dist, values)

    batches_n = cpus * 10
    batch_size = int(len(labels) / batches_n)

    labels_tmp = []  # List of lists ...
    [labels_tmp.append(batch) for batch in util.chunks(labels, batch_size)]

    # partial distances given current labels
    dists = pool.map(func, labels_tmp)

    # close fork
    pool.close()
    pool.join()

    # init dict by first batch res
    res_dict = {}

    [res_dict.update({item[1]: (item[0], item[2])}) for item in dists[0]]

    [res_dict.update({item[1]: (item[0], item[2])}) for sublist in dists[1:]
     for item in sublist if item[0] < res_dict[item[1]][0]]

    return res_dict


def get_candidates(vals):
    """
    :param vals: cell values
    :return: closest label candidate from the full file
    """
    # candidates dict for the given str
    final_res = {}
    i = 0  # represents chunk index, not really important, just to keep track

    with open(join(ASSET_PATH, 'labels.txt'), encoding='utf8', errors='ignore') as f:

        for chunk in load_file(f, lazy=True):
            # partial res candidate from the current chunk of file for the given values
            partial_res = get_nearest_candidate(chunk, vals)
            print('Chunk {} and looking for #{} values'.format(i, len(values)))
            if i == 0:
                # init final_res_dict if first chunk of file
                [final_res.update({k: v}) for k, v in partial_res.items()]
            else:
                # conditional append if new dist is less of what we have already
                print("Min dist is found this chunk")
                [final_res.update({k: v}) for k, v in partial_res.items() if v[0] < final_res[k][0]]

            # short circuit on 1 edit letter
            tmp_vals = [k for k, v in partial_res.items() if v[0] > 1]
            if len(tmp_vals) < len(vals):  # some candidates with distance 1 are found and excluded
                print('values reduced - short circuit')
                vals = tmp_vals  # update vals list in the next call.

            if len(tmp_vals) == 0:
                print('all values are processed ... break')
                break

            print('Chunk {} done.'.format(i))
            i = i + 1

    [final_res.update({k: v[1]}) for k, v in final_res.items()]
    return final_res


def test():
    # Court cases from table 3WJT10EJ.csv 2020 R2
    vals = ['Spaziano . Florida',
            'Smith v/ Maryland',
            'SEC v. Texas Gulf Sumphur Co.',
            'Reieer v. Thompso',
            'Reed v. Pennsylvania Railroad Compan|',
            'Building Service Employees International Union Local 262 v/ Gazzam',
            'Ramspeck v. Federal Trial Exainers Conference',
            'Cowma Dairy Company v. United States',
            'Noswood v. Kirkpatrick',
            'Mongomery Building & Construction Trades Council v. Ledbetter Erection Company',
            'Southern Pacfic Company v. Gileo',
            'Colgate-Palmolive-Peft Company v. National Labor Relations Board',
            'Unitee States v. United States Smelting Refining',
            'Poizzi v. Cowles Magazies']
    expected = ['Spaziano v. Florida',
                'Smith v. Maryland',
                'SEC v. Texas Gulf Sulphur Co',
                'Reider v. Thompson ',
                'Reed v. Pennsylvania Railroad Company',
                'Building Service Employees International Union Local 262 v. Gazzam',
                'ramspeck v. federal trial examiners conference',
                'Bowman Dairy Company v. United States',
                'Norwood v. Kirkpatrick',
                'Montgomery Building & Construction Trades Council v. Ledbetter Erection Company',
                'Southern Pacific Company v. Gileo',
                'Colgate-Palmolive-Peet Company v. National Labor Relations Board',
                'United States v. United States Smelting Refining',
                'Polizzi v. Cowles Magazines']

    util_log.start("test")

    # Loads file once and get a list of predicted
    res = get_candidates(vals)

    cnt = 0
    for val, exp in zip(vals, expected):
        util_log.info("'{}' is corrected as --> '{}'".format(res[val], expected))
        if res[val].lower() == exp.lower():  # normalize case insensitive
            cnt = cnt + 1
    util_log.stop("test")


def load_unique_values():
    with open(join(ASSET_PATH, 'unique_values.txt'), 'r', encoding='utf8', errors='ignore') as file:
        content = file.read()
    values = content.split('\n')
    return values


def fix_unique_values(values):
    return [fix_text(val, normalization='NFKC') for val in values]


# def save(res):
#     content = '\n'.join(['{},{}'.format(k, v) for k, v in res.items()])
#     with open(join(realpath('.'), 'assets', 'autocorrected_values.txt'), 'w', encoding='utf8', errors='ignore') as file:
#         file.write(content)


if __name__ == '__main__':
    util_log.start('load_unique_values')
    original_values = load_unique_values()
    util_log.stop('load_unique_values')

    util_log.start('fix_unique_values')
    values = fix_unique_values(original_values)
    util_log.stop('fix_unique_values')

    util_log.start('get_candidates')
    res = get_candidates(values)
    util_log.stop('get_candidates')
    #
    # util_log.start('save')
    # save(res)
    # util_log.start('save')
