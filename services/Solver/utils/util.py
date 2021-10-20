import os
from os.path import join, exists
import config

def weighted_sort(lst):
    freq_dict = {}
    for el in lst:
        if el not in freq_dict:
            freq_dict[el] = 0
        freq_dict[el] += 1

    sorted_dict = {}
    for w in sorted(freq_dict, key=freq_dict.get, reverse=True):
        sorted_dict[w] = freq_dict[w]

    return sorted_dict


def get_most_frequent(lst):
    if len(lst) == 0:
        return []

    sorted_dict = weighted_sort(lst)
    # get highest val
    most_freq_key = next(iter(sorted_dict))
    most_freq_val = sorted_dict[most_freq_key]

    res = []
    # get ties if exists
    for key, val in sorted_dict.items():
        if val == most_freq_val:
            res = res + [key]
    return res


# load stop words
words_path = join(config.ASSET_PATH, 'stopwords.txt')
words = ""
with(open(words_path, 'r')) as file:
    words = file.read()
STOP_WORDS = words.split('\n')


def load_stop_words():
    return STOP_WORDS


# TODO: Deprecate this
def assert_dir(dir_path):
    """make sure the folder exists and is writeable to us"""
    # make sure the file exists
    if not exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)  # recursive mkdir
    # check, if we can write to it
    if not os.access(dir_path, os.W_OK):
        raise PermissionError('Cannot access folder {}'.format(dir_path))