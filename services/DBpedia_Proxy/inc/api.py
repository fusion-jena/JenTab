from .aggregate import aggregateByKeys, formatOutput
from .query import query, runQuerySingleKey
import inc.cache

# init caches
cachePopularity = inc.cache.Cache('popularity', ['base'])


async def get_popularity_for_lst(entities):
    """
    retrieve the popularity for the given entities
    popularity is the number of objects linking to an entity
    """
    res = await runQuerySingleKey(cachePopularity, entities, """
        SELECT DISTINCT ?base (COUNT(?parent) AS ?popularity)
        WHERE
        {
          VALUES ?base { %s } .
          ?parent ?prop ?base .          
        }
        GROUP BY ?base
    """)
    # Some cases returned None case and casued many exception, we handle it as set default value
    # NY: I looked for ISNULL and COALESCE but didn't work. So, I handled in code.
    if res is None:
        return 0
    else:
        return res
