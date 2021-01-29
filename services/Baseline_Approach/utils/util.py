import os
from os.path import join, realpath, exists


def weighted_sort(lst):
    unique_elems = list(set(lst))
    freq_dict = {}
    for uelem in unique_elems:
        freq_dict[uelem] = 0
        for elem in lst:
            if elem == uelem:
                freq_dict[uelem] = freq_dict[uelem] + 1

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
words_path = join(realpath('.'), 'assets', 'stopwords.txt')
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