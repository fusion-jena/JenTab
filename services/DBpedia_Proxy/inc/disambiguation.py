from .query import runQuerySingleKey
import inc.cache
import config

# init caches
cacheDisambiguation = inc.cache.Cache('disambiguation', ['base'])
cacheDisambiguationOld = inc.cache.Cache('disambiguation_old', ['base'])


async def resolve_disambiguations(entities):
    """
    Get disambiguation values for a given list
    """

    # TODO: this should also extend to properties like dbo:wikiPageWikiLink as can be seen, e.g., on https://dbpedia.org/page/CR7
    #   but how to make sure we're only looking at disambiguation pages here
    #   and does not catch arbitrary page links on other wikipages?

    res = await runQuerySingleKey(cacheDisambiguation, entities, f"""
      PREFIX dbo: <http://dbpedia.org/ontology/>
      SELECT DISTINCT ?base ?target
      WHERE
      {{
        VALUES ?base {{ %s }} .
        ?base dbo:wikiPageDisambiguates ?target .
      }}
      LIMIT { config.RESULTS_LIMIT }
    """)

    return res
