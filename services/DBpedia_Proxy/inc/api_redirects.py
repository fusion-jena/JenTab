from .query import runQuerySingleKey
import inc.cache
import config

# init caches
cacheRedirect = inc.cache.Cache('redirects', ['base'])


async def resolve_redirects(entities):

    """
    resolve possible redirects of pages
    """

    # binding the base as redirect to enable caching of non-redirects
    res = await runQuerySingleKey(cacheRedirect, entities, f"""
      PREFIX dbo: <http://dbpedia.org/ontology/>

      SELECT ?base ?redirect
      WHERE {{

        VALUES ?base {{ %s }} .
        OPTIONAL {{ ?base dbo:wikiPageRedirects ?actualRedirect . }}
        BIND ( IF (BOUND (?actualRedirect ), ?actualRedirect, ?base) as ?redirect) .

      }}
      LIMIT { config.RESULTS_LIMIT }
    """)

    return res
