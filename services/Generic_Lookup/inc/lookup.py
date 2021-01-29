import asyncio
import os
import urllib
import inc.cache
import config


# cache of results
cache = inc.cache.Cache('lookup', ['needle'])

# terms we dont want to run
INVALID_TERMS = set(["", "nan"])


async def lookup(terms):
    """
    run Wikidata lookups for the requested terms
    """

    # run lookups for all terms in parallel
    terms = list(set(terms))
    reqs = [lookup_single(term) for term in terms]
    resp = await asyncio.gather(*reqs)

    # assemble result
    res = {}
    for r in resp:
        res = {**res, **r}

    # done
    return res


async def lookup_single(term):
    """
    run a single Wikidata lookup
    """

    # check, if there is something in the cache
    cached = cache.get({'needle': term})
    if cached:
        return {term: cached}
    else:
        return {}
