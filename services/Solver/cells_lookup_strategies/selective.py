from cells_lookup_strategies.strategy import *
from config import Selective_priority, CLEAN_CELL_SEPARATOR


class SelectiveLookup(CellsStrategy):
    def __init__(self):
        CellsStrategy.__init__(self, name='selective', priority=Selective_priority)

    def __get_start_end(self, txt):
        """
        Looks for different brackets inside the text
        """
        _open  = ['(', '{', '<', '[']
        _close = [')', '}', '>', ']']
        for o, c in zip(_open, _close):
            if o in txt and c in txt:
                s = txt.find(o)
                e = txt.find(c)
                return s, e
        return -1, -1  # Not found case

    def process_cell_values(self, cell):
        """
        Select a part from the original cell
        """
        original_cell_val = cell['value']
        clean_cell_val = cell['clean_val']
        s, e = self.__get_start_end(original_cell_val)
        if s > -1 and e > -1:
            exclude_part = original_cell_val[s + 1:e]
            exclude_tokens = exclude_part.split(CLEAN_CELL_SEPARATOR)
            clean_tokens = clean_cell_val.split(CLEAN_CELL_SEPARATOR)
            return ' '.join([c for c in clean_tokens if c not in exclude_tokens])
        return None


# Some tests ...
if __name__ == '__main__':
    test = "Super Mairo's (Wii Points 200)"
    # test = "Super Mairo's [Wii Points 200]"
    # test = "Super Mairo's {Wii Points 200}"
    # test = "Super Mairo's <Wii Points 200>"
    # test = "Super Mairo's (Wii Points 200>"
    test_clean = "Super Mairo's Wii Points 200"
    cell = {'value': test, 'clean_val': test_clean}
    print(SelectiveLookup().process_cell_values(cell))
