import re
import config
from utils.vec_manager import *
import inc.cache

# cache of results
cache = inc.cache.Cache('terms', ['term'])

class W2VCorrection():
    def __init__(self, model1):
        self.model = model1
        self.WORDS = self.__get_words()

    def __get_words(self):
        words = self.model.index2word

        w_rank = {}
        for i, w in enumerate(words):
            w_rank[w] = i

        WORDS = w_rank
        return WORDS

    def correct_word(self, word):
        words = word.split(config.CLEAN_CELL_SEPARATOR)
        lst = []
        for word in words:
            if word in self.WORDS:  # No need to check the edits for known words!
                lst = lst + [word]
            else:
                lst = lst + [self.correction(word)]
        res = "{}".format(config.CLEAN_CELL_SEPARATOR).join(lst)
        cache.set({'term': word}, [res])
        return res

    # Methods related to correction probability
    def words(self, text):
        return re.findall(r'\w+', text.lower())

    def P(self, word):
        "Probability of `word`."
        # use inverse of rank as proxy
        # returns 0 if the word isn't in the dictionary
        return - self.WORDS.get(word, 0)

    def correction(self, word):
        "Most probable spelling correction for word."
        return max(self.candidates(word), key=self.P)

    def candidates(self, word):
        "Generate possible spelling corrections for word."

        # Limit candidates generation to only one edit distance
        return self.known(self.edits1(word)) or [word]
        # return (self.known([word]) or self.known(self.edits1(word)) or self.known(self.edits2(word)) or [word])

    def known(self, words):
        "The subset of `words` that appear in the dictionary of WORDS."
        return set(w for w in words if w in self.WORDS)

    def edits1(self, word):
        "All edits that are one edit away from `word`."
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    # def edits2(self, word):
    #     "All edits that are two edits away from `word`."
    #     return (e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))


if __name__ == '__main__':
    model = VecIO().load_model()
    correctObj = W2VCorrection(model)

    for word in ['Köln', 'Tübingen', 'Amlie', 'Mario\'s', 'Rashmon', 'L?eon']:
        print(correctObj.correct_word(word))
