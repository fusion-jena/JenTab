from inc.custom_parser import CustomParser
from utils import util
import const.col_types as col_types


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

    return {'clean': clean_lst}


def __fix_date(list_values):
    """
    Finds first date match in each value
    i.e., clean_cell = 2010-11-23 November 23, 2010
    res = 2010-11-23
    """
    clean_lst = [util.find_date(val) for val in list_values]
    return {'clean': clean_lst}


def __fix_quantity(list_values):
    clean_lst = [util.find_num(val) for val in list_values]
    return {'clean': clean_lst}


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
    return {'clean': list_values}


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

    fixed1 = fix_any(lst)['clean']

    fixed2 = fix_specific(fixed1, col_type)['clean']

    for v, f1, f2 in zip(lst, fixed1, fixed2):
        print('{}, \t {}, \t {}'.format(v, f1, f2))


if __name__ == '__main__':
    test_specific()
