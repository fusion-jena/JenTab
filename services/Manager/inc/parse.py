import config
import os
import pandas as pd


def parse(path):
    """load a file and parse it with pandas"""

    # get header row
    with open(path, 'r', encoding='utf8') as file:
        header = file.readline().strip().split(',')

    # TODO: Check Table Orientation
    orientation = "Horizontal"

    # get contents
    cols = []
    try:
        df = pd.read_csv(path, names=header, keep_default_na=False)
        for col in df.columns:
            cols = cols + [df[col].to_list()]
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
