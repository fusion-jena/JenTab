import config
import pandas as pd


def parse(path, hasHeaders=True):
    """
    load a file and parse it with pandas

    @param    {String}  path        path to the file
    @param    {Boolean} hasHeaders  is the first row a header row?
    @returns  {dict}                parsed file content
    """

    # get header row
    if hasHeaders:
        with open(path, 'r', encoding='utf8') as file:
            header = file.readline().strip().split(',')

    # TODO: Check Table Orientation
    orientation = "Horizontal"

    # get contents
    cols = []
    try:

        if hasHeaders:
            df = pd.read_csv(path, names=header, keep_default_na=False)
        else:
            df = pd.read_csv(path, header=None, keep_default_na=False)

        for col in df.columns:
            cols = cols + [df[col].to_list()]

        header = [ [] for col in df.columns ]

    except Exception as e:
        print(e)
        # if pandas failed, we parse manually
        cols = manual_parse(path)

    res = {'orientation': orientation, 'header': header, 'cols': cols}
    return res


def manual_parse(path):
    """manually parse csv file contents, if pandas failed"""

    with open(path, 'r', encoding='utf8') as file:
        lines = file.read().split('\n')
    cells = [line.strip().split(',') for line in lines]
    cnt = [len(line_cells) for line_cells in cells]
    cols_num = max(get_most_frequent(cnt))
    if cols_num == 1:
        cnt = [c for c in cnt if c != 1]
        cols_num = max(get_most_frequent(cnt))

    cols = []
    for i in range(cols_num):
        col = []
        for row in cells:
            try:
                col = col + [row[i]]
            except:
                col = col + [""]
        cols = cols + [col]
    return cols


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