from .utils.custom_parser import CustomParser
from .utils import util
from .const import col_types
import re
import config as globalConfig
import calendar

def fix_any(list_values):
    """ Applies a blind fixes on the given data list"""

    # Original values are only fixed for encoding issues
    list_values = [util.decode(val) for val in list_values]

    # clean NaN and artificial empty cells
    clean_list = util.clean_data(list_values)

    # Restore missing spaces in values
    clean_list = [CustomParser.parse(val) for val in clean_list]

    # prepare result
    clean_cells = {'fixed_original': list_values, 'clean': clean_list}
    return clean_cells


# ------------------ fix_specific ------------------------------

def __fix_object(list_values):
    # remove some special chars from a string
    clean_lst = [util.remove_special_chars(val) for val in list_values]

    if globalConfig.ENABLE_BIODIV_DICT:
        # special case for Biodiversity
        for i, val in enumerate(clean_lst):
            if "species:" in val and "sub:" in val:
                # parts = val.split(":")
                parts = re.split(' |:|', val)
                clean_lst[i] = parts[1] + ' ' + parts[3]

        # convert Unknown words to None
        unknowns = ['unknown', 'undetermined', 'N/A', '?']
        for i, val in enumerate(clean_lst):
            for unknown in unknowns:
                if val is not None and unknown in val.lower():
                    clean_lst[i] = ''

        # Fix nested entity (first-fit strategy)
        # split the actual value and take the first part (if possible)
        # try split by /, (), -
        separators = ['/', ' - ', '(']
        for i, val in enumerate(clean_lst):
            for sep in separators:
                if val is not None and val.count(sep) == 1:
                    clean_lst[i] = val.split(sep)[0]
                    # consider only one separator that might co-occur
                    break

    return clean_lst


def __fix_date(list_values):
    """
    Finds first date match in each value
    i.e., clean_cell = 2010-11-23 November 23, 2010
    res = 2010-11-23
    """
    clean_lst = [util.find_date(val) for val in list_values]
    return clean_lst


def __fix_quantity(list_values):
    clean_lst = [util.find_num(val) for val in list_values]

    if globalConfig.ENABLE_BIODIV_DICT:
        # fix month if the header says month and listing some numbers
        if clean_lst[0].lower() == 'month':
            for i, val in enumerate(clean_lst):
                if val.isdigit() and 12 >= int(val) >= 1:
                    clean_lst[i] = calendar.month_name[int(val)]

    return clean_lst


def fix_specific(list_values, col_type):
    """
    specific clean up for the following col_type
    list_values should be passed by fix_any phase.
    """
    if col_type == col_types.OBJECT or col_type == col_types.OTHER:
        return __fix_object(list_values)
    if col_type == col_types.DATE:
        return __fix_date(list_values)
    if col_type == col_types.QUANTITY:
        return __fix_quantity(list_values)

    # if nothing specified, then the general fixes is enough
    return list_values


def test_any():
    text = ["2010-11-23November 23, 2010",
            "36Â°30â€²29â€³N 80Â°50â€²00â€³Wï»¿ / ï»¿36.50806Â°N 80.83333Â°Wï»¿ / 36.50806; -80.83333",
            "L?eon The Professional", 'KÃ¼hn', 'TÃ¼bingen', 'Rashmon', 'Amlie', 'Mario\'s Game', "[USA Toady]",
            "Micro-Services is Hard!"]
    print(fix_any(text))


def test_specific():
    # col_type = 'DISTANCE'
    #
    # lst = ['1,025 m (3,363 ft)', '1,025 m (3,363 ft)',
    #         '1,025 m (3,363 ft)', '1,025 m (3,363 ft)',
    #         '1,025 m (3,363 ft)', '406.3 m (1,333 ft)',
    #         '406.3 m (1,333 ft)', 'Noise here']

    # col_type = 'DATE'
    #
    # lst = ['2010-11-23November 23, 2010', '2010/11/24November 24, 2011',
    #        'Today 9:00 PM', '5-11-2010',
    #        '11', 'Noise here']

    col_type = 'OBJECT'

    lst = ['Picu PÄƒtruÅ£', 'anonymous', 'Jacquemart de Hesdin',
           'Limbourg brothers', 'Rogier van der Weyden', 'Gottlieb Schiffner',
           'Alessandro Merli', 'Louis-FranÃ§ois Marteau']

    fixed1 = fix_any(lst)

    fixed2 = fix_specific(fixed1, col_type)

    for v, f1, f2 in zip(lst, fixed1, fixed2):
        print('{}, \t {}, \t {}'.format(v, f1, f2))


def test_specific2():
    col_type = 'OBJECT'
    lst = ['Unknown Species']
    fixed = fix_specific(lst, col_type)
    for v, f1 in zip(lst, fixed):
        print('{}, \t {}'.format(v, f1))


if __name__ == '__main__':
    # test_specific()
    test_specific2()
