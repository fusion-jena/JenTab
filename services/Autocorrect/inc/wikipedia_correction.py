from collections import Counter
import re
from os.path import  join
from config import ASSET_PATH

class WikipediaCorrection(object):
    def __init__(self):
        self.Vocab = []     # Vocab list
        self.vocab_n = None  # Vocab length
        self.probs = {}     # Probabilities dict
        self.init_vocab()

    def init_vocab(self):
        """ Loads probabilities dict, vocab list and calculates its length """
        with open(join(ASSET_PATH, 'wiki_en_vocab_probs.csv'), 'r') as file:
            content = file.read().splitlines()

        for line in content:
            k, v = line.split(',')
            self.probs[k] = float(v)
            self.Vocab.append(k)
        self.vocab_n = len(self.Vocab)

    def __get_word_splits(self, word):
        return [(word[:i], word[i:]) for i in range(len(word) + 1)]

    def __delete_letter(self, split_l):
        return [L + R[1:] for L, R in split_l if R]

    def __switch_letter(self, split_l):
        return [L + R[1] + R[0] + R[2:] for L, R in split_l if len(R) > 1]

    def __replace_letter(self, split_l):
        letters = 'abcdefghijklmnopqrstuvwxyz'
        return [L + c + R[1:] for L, R in split_l for c in letters if R and c != R[0]]

    def __insert_letter(self, split_l):
        letters = 'abcdefghijklmnopqrstuvwxyz'
        return [L + c + R[0:] for L, R in split_l for c in letters]

    def edit_one_letter(self, word, allow_switches=True):
        """
           Input:
               word: the string/word for which we will generate all possible wordsthat are one edit away.
           Output:
               edit_one_set: a set of words with one possible edit. Please return a set. and not a list.
           """
        split_l = self.__get_word_splits(word)
        all_l = self.__insert_letter(split_l) + self.__replace_letter(split_l) + self.__delete_letter(split_l)
        if allow_switches:
            all_l = all_l + self.__switch_letter(split_l)
        edit_one_set = set(all_l)

        return edit_one_set

    def edit_two_letters(self, word, allow_switches=True):
        """
            Input:
                word: the input string/word
            Output:
                edit_two_set: a set of strings with all possible two edits
        """

        edit_two_set = set(
            [e2 for e1 in self.edit_one_letter(word, allow_switches) for e2 in self.edit_one_letter(e1, allow_switches)])

        return edit_two_set

    def __filter_edits(self, edits, n):
        suggestions = {}
        # [suggestions.append((e, self.probs[e])) for e in edits if e in self.Vocab]

        filtered_edits = [e for e in edits if e in self.Vocab]
        for e in filtered_edits:
            suggestions[e] = self.probs[e]
        counter = Counter(suggestions)
        n_best = counter.most_common(n)
        return n_best

    def get_corrections(self, word, n=1):
        """
            Input:
                word: a user entered string to check for suggestions
                n: number of possible word corrections you want returned in the dictionary
            Output:
                n_best: a list of tuples with the most probable n corrected words and their probabilities.
        """

        suggestions = {}
        n_best = []
        word = word.lower()
        # First Priority
        if word in self.Vocab:
            # suggestions.append((word, self.probs[word]))
            return word, self.probs[word]

        # 2nd Priority is less edits a.k.a edit one letter
        edits = self.edit_one_letter(word)
        n_best = self.__filter_edits(edits, n)
        if len(n_best) > 0:
            return n_best[0] # Short Circuit

        # 3rd Priority
        edits = self.edit_two_letters(word)
        n_best = self.__filter_edits(edits, n)
        if len(n_best) > 0:
            return n_best[0]  # Short Circuit
        else:
            return word, 0.0 # Worst case, if nothing worked, return the word itself, prob = 0.0


if __name__ == '__main__':
    print("==============================Test 1=========================================")
    wikiCorrect = WikipediaCorrection()
    tmp_word = "at"
    tmp_edit_one_set = wikiCorrect.edit_one_letter(tmp_word)
    # turn this into a list to sort it, in order to view it
    tmp_edit_one_l = sorted(list(tmp_edit_one_set))

    print(f"input word {tmp_word} \nedit_one_l \n{tmp_edit_one_l}\n")
    print(f"The type of the returned object should be a set {type(tmp_edit_one_set)}")
    print(f"Number of outputs from edit_one_letter('at') is {len(wikiCorrect.edit_one_letter('at'))}")
    """
    *********** Excepected Output **************
    input word at 
    edit_one_l 
    ['a', 'aa', 'aat', 'ab', 'abt', 'ac', 'act', 'ad', 'adt', 'ae', 'aet', 'af', 'aft', 'ag', 'agt', 'ah', 'aht', 'ai', 'ait', 'aj', 'ajt', 'ak', 'akt', 'al', 'alt', 'am', 'amt', 'an', 'ant', 'ao', 'aot', 'ap', 'apt', 'aq', 'aqt', 'ar', 'art', 'as', 'ast', 'ata', 'atb', 'atc', 'atd', 'ate', 'atf', 'atg', 'ath', 'ati', 'atj', 'atk', 'atl', 'atm', 'atn', 'ato', 'atp', 'atq', 'atr', 'ats', 'att', 'atu', 'atv', 'atw', 'atx', 'aty', 'atz', 'au', 'aut', 'av', 'avt', 'aw', 'awt', 'ax', 'axt', 'ay', 'ayt', 'az', 'azt', 'bat', 'bt', 'cat', 'ct', 'dat', 'dt', 'eat', 'et', 'fat', 'ft', 'gat', 'gt', 'hat', 'ht', 'iat', 'it', 'jat', 'jt', 'kat', 'kt', 'lat', 'lt', 'mat', 'mt', 'nat', 'nt', 'oat', 'ot', 'pat', 'pt', 'qat', 'qt', 'rat', 'rt', 'sat', 'st', 't', 'ta', 'tat', 'tt', 'uat', 'ut', 'vat', 'vt', 'wat', 'wt', 'xat', 'xt', 'yat', 'yt', 'zat', 'zt']
    
    The type of the returned object should be a set <class 'set'>
    Number of outputs from edit_one_letter('at') is 129
    """
    print("==============================Test 2=========================================")
    tmp_edit_two_set = wikiCorrect.edit_two_letters("a")
    tmp_edit_two_l = sorted(list(tmp_edit_two_set))
    print(f"Number of strings with edit distance of two: {len(tmp_edit_two_l)}")
    print(f"First 10 strings {tmp_edit_two_l[:10]}")
    print(f"Last 10 strings {tmp_edit_two_l[-10:]}")
    print(f"The data type of the returned object should be a set {type(tmp_edit_two_set)}")
    print(f"Number of strings that are 2 edit distances from 'at' is {len(wikiCorrect.edit_two_letters('at'))}")
    """
    *********** Excepected Output **************
    Number of strings with edit distance of two: 2654
    First 10 strings ['', 'a', 'aa', 'aaa', 'aab', 'aac', 'aad', 'aae', 'aaf', 'aag']
    Last 10 strings ['zv', 'zva', 'zw', 'zwa', 'zx', 'zxa', 'zy', 'zya', 'zz', 'zza']
    The data type of the returned object should be a set <class 'set'>
    Number of strings that are 2 edit distances from 'at' is 7154
    """
    print("==============================Test 3=========================================")

    vals = ['Spaziano . Florida', \
            'Smith v/ Maryland', \
            'SEC v. Texas Gulf Sumphur Co.', \
            'Reieer v. Thompso', \
            'Reed v. Pennsylvania Railroad Compan|', \
            'Building Service Employees International Union Local 262 v/ Gazzam', \
            'Ramspeck v. Federal Trial Exainers Conference', \
            'Cowma Dairy Company v. United States', \
            'Noswood v. Kirkpatrick', \
            'Mongomery Building & Construction Trades Council v. Ledbetter Erection Company', \
            'Southern Pacfic Company v. Gileo', \
            'Colgate-Palmolive-Peft Company v. National Labor Relations Board', \
            'Unitee States v. United States Smelting Refining', \
            'Poizzi v. Cowles Magazies']
    expected = ['Spaziano v. Florida', \
                'Smith v. Maryland', \
                'SEC v. Texas Gulf Sulphur Co', \
                'Reider v. Thompson ', \
                'Reed v. Pennsylvania Railroad Company', \
                'Building Service Employees International Union Local 262 v. Gazzam', \
                'ramspeck v. federal trial examiners conference', \
                'Bowman Dairy Company v. United States', \
                'Norwood v. Kirkpatrick', \
                'Montgomery Building & Construction Trades Council v. Ledbetter Erection Company', \
                'Southern Pacific Company v. Gileo', \
                'Colgate-Palmolive-Peet Company v. National Labor Relations Board', \
                'United States v. United States Smelting Refining', \
                'Polizzi v. Cowles Magazines']
    cnt = 0
    for val, exp in zip(vals, expected):
        words = re.findall(r'\w+', val)
        # fix word by word in the given value
        corrections = [wikiCorrect.get_corrections(word) for word in words]
        res = ' '.join([c[0] for c in corrections])
        print(res)
        if res.lower() == exp.lower(): # normalize case insenstive
            cnt = cnt + 1
    print((cnt / len(vals)) * 100)