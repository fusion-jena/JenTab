from autocorrect import Speller


spell = Speller()


def correct(word):
    return spell(word)
