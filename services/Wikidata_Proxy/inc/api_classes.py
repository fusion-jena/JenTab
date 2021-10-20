import asyncio
from .query import *
import inc.cache
from util.util import getWikiID

cacheSubclass = inc.cache.Cache('subclass', ['base'])
cacheSuperclass = inc.cache.Cache('superclass', ['base'])


async def get_subclasses(klass):
    """retrieve all subclasses for the given one"""

    # remove wikidata prefix
    klass = getWikiID(klass)

    # check the cache
    cached = cacheSubclass.get({'base': klass})
    if cached:
        return {klass: cached}

    # prepare query
    statement = """
                SELECT ?subclass ?subclassLabel
                WHERE {
                  ?subclass wdt:P279 wd:%s .
                  SERVICE wikibase:label {bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".}
                }""" % (klass)

    # run it
    resp = await query(statement)

    # store in cache
    if resp:
        cacheSubclass.set({'base': klass}, resp)

    # done
    return {klass: resp}


async def get_parents_for_lst(klasses):
    """Get most generic type for a given entity mention P279 in Wikidata"""

    res = await runQuerySingleKey(cacheSuperclass, klasses, """
      SELECT ?base ?parent ?parentLabel
      WHERE {
        VALUES ?base { %s } .
        ?base wdt:P279 ?parent .
        SERVICE wikibase:label {bd:serviceParam wikibase:language "en".}
      }
    """)
    return res
