from .query import runQuerySingleKey
import inc.cache
import config

# init caches
cacheDisambiguation = inc.cache.Cache('disambiguation', ['base'])


async def resolve_disambiguations(entities):
    """
    Get disambiguation values for a given list
    """

    # no need so far in Wikidata, so this is left unimplemented

    return {}
