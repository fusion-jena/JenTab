from autocorrect import Speller
import inc.cache

spell = Speller()

# cache of results
cache = inc.cache.Cache('terms', ['term'])

def correct(word):
    res = spell(word)
    cache.set({'term': word}, [res])
    return res
