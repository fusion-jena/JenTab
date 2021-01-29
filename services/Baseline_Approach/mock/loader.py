import json
from os.path import join, realpath
import config


file_name = config.TEST_FILE

def load_file():
    """load the input for the currently set table"""
    file_path = join(realpath('.'), 'mock', file_name + '.json')
    with open(file_path, 'r') as file:
        processed_table = json.load(file)
        return processed_table


def load_targets():
    """load the targets for the currently set table"""
    file_path = join(realpath('.'), 'mock', file_name + '.targets.json')
    with open(file_path, 'r') as file:
        processed_table = json.load(file)
        return processed_table
