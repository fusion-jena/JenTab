import os
from .query import runQuerySingleKey
import inc.cache
import config

# init caches
cacheSameAs = inc.cache.Cache('samAs1', ['base'])


async def get_sameAs_for_lst(entities):

    """
    Get the direct types and all their parents
    aka simulate a reasoner and get all classes of the given entities
    """

    res = await runQuerySingleKey(cacheSameAs, entities, f"""
      SELECT ?base ?map
      WHERE {{

        VALUES ?base {{ %s }} .
        ?map owl:sameAs ?base .        

      }}
      LIMIT { config.RESULTS_LIMIT }
    """,printIt=True)

    return res