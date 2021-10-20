import json
import os



def load_file(file_name):
    """load the input for the currently set table"""
    file_path = os.path.join(os.path.realpath('.'), 'mock', file_name + '.json')
    with open(file_path, 'r') as file:
        processed_table = json.load(file)
        return processed_table


def load_targets(file_name):
    """load the targets for the currently set table"""
    file_path = os.path.join(os.path.realpath('.'), 'mock', file_name + '.targets.json')
    with open(file_path, 'r') as file:
        processed_table = json.load(file)
        return processed_table


def load_gt(file_name):
    """load ground truth data, if existent"""
    file_path = os.path.join(os.path.realpath('.'), 'mock', file_name + '.gt.json')
    if os.path.exists( file_path ):
        with open(file_path, 'r') as file:

            # load file
            processed_table = json.load(file)

            # convert ids to numbers
            if 'cea' in processed_table:
                for item in processed_table['cea']:
                    item['col_id'] = int(item['col_id']) if item['col_id'] is not None else None
                    item['row_id'] = int(item['row_id']) if item['row_id'] is not None else None
            if 'cta' in processed_table:
                for item in processed_table['cta']:
                    item['col_id'] = int(item['col_id']) if item['col_id'] is not None else None
            if 'cpa' in processed_table:
                for item in processed_table['cpa']:
                    item['sub_id'] = int(item['sub_id']) if item['sub_id'] is not None else None
                    item['obj_id'] = int(item['obj_id']) if item['obj_id'] is not None else None

            return processed_table
    else:
        return None
