from .solver import fix_any, fix_specific


def fix_cell_lst(col_cells):
    """Clean a list of cells - column cells"""

    # List of strings
    clean_cells = fix_any(col_cells)
    return clean_cells


def specific_clean_cell_lst(col_cells, col_type):
    """Clean a list of cells - column cells"""
    # List of strings
    clean_cells = fix_specific(col_cells, col_type)
    return clean_cells


if __name__ == '__main__':
    lst = ["it&#x2019;s", 'TÃ¼bingen', 'Rashmon', "   I Love     Egypt.              ", "  Barak Obama"]
    print(fix_any(lst))