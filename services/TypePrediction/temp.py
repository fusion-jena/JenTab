from collections import Counter

from solver import get_type_lst
from os import listdir
from os.path import join, realpath
import json

dir_path = join(realpath('.'), 'json_tables', 'Round1')
def get_cells(file):
    res = {}
    with(open(join(dir_path, file), 'r')) as jfile:
        content = json.load(jfile)
        data = content['data']
        for key, val in data.items():
            # if val['type'] == 'OBJECT':
            res[key] = [cell.replace('_', ' ') for cell in val['clean_cell_vals']]
    return res

def set_type(file, col_key, type):
    with(open(join(dir_path, file), 'r')) as jfile:
        content = json.load(jfile)
    content['data'][col_key]['type'] = type
    with(open(join(dir_path, file), 'w')) as wjfile:
        json.dump(content, wjfile)

def get_most_frequent(lst):
    most_common, num_most_common = Counter(lst).most_common(1)[0]  # 4, 6 times
    return most_common

def reclean():
    files = listdir(dir_path)
    # files = ['1438042986423_95_20150728002306-00329-ip-10-236-191-2_805336391_10.json']
    for file in files:
        old_clean_dict = get_cells(file)
        for col_key, cells_val in old_clean_dict.items():
            types = get_type_lst(cells_val)['res']
            type = get_most_frequent(types)
            set_type(file, col_key, type)

if __name__ == '__main__':
    reclean()