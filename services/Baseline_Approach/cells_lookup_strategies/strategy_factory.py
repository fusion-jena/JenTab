from cells_lookup_strategies.generic import GenericLookup
from cells_lookup_strategies.full_cell import FullCellLookup
from cells_lookup_strategies.all_tokens import AllTokensLookup
from cells_lookup_strategies.individual_tokens import IndividualTokensLookup
from cells_lookup_strategies.selective import SelectiveLookup
from cells_lookup_strategies.autocorrection import AutocorrectLookup


class StrategyFactory(object):
    def __init__(self):
        self.strategies_n = None
        self.strategies = None
        self.init_strategies()
        self.__sort()

    def init_strategies(self):
        self.strategies = []
        self.strategies = self.strategies + [GenericLookup()]
        self.strategies = self.strategies + [FullCellLookup()]
        self.strategies = self.strategies + [AllTokensLookup()]
        self.strategies = self.strategies + [IndividualTokensLookup()]
        self.strategies = self.strategies + [SelectiveLookup()]
        self.strategies = self.strategies + [AutocorrectLookup()]
        self.strategies_n = len(self.strategies)

    def __sort(self):
        self.strategies.sort(key=lambda x: x.priority)

    def getPriorities(self):
        """
        get an ordered list of all priorities registered
        """
        prios = [x.priority for x in self.strategies]
        return sorted(prios)

    def getByPriority(self, prio):
        """
        retrieve all strategies with the given priority
        """
        return [x for x in self.strategies if x.priority == prio]

    def get_highest_priority(self):
        return self.strategies[0]

    def get_remaining_priority(self):
        return self.strategies[1:self.strategies_n]


if __name__ == '__main__':
    fact = StrategyFactory()
    x = fact.get_highest_priority()
    print(x.priority)
    x = fact.get_remaining_priority()
    [print(xi) for xi in x]
