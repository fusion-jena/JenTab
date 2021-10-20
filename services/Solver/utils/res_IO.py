from config import TABLE_RES_PATH
import json
import os
from os.path import join, exists


def set_res(tablename, res_dict):
    """
    Sets prepared res_dict under res_path as json files
    """

    with open(join(TABLE_RES_PATH, tablename + '.json'), 'w', encoding='utf8') as file:
        json.dump(res_dict, file, indent=4, default=str)


def get_res(tablename, clean=True):
    """
    Gets the last saved file of the res_dict for a given table name,
    it will delete the file if clean
    """

    with open(join(TABLE_RES_PATH, tablename + '.json'), 'r') as file:
        res_dict = json.load(file)

    if clean:
        os.remove(join(TABLE_RES_PATH, tablename + '.json'))
    return res_dict


def res_exists(tablename):
    return exists(join(TABLE_RES_PATH, tablename + '.json'))
