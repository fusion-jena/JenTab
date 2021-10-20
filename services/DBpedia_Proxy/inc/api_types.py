import os
from .query import runQuerySingleKey
import inc.cache
import config

# init caches
cacheAncestors = inc.cache.Cache('ancestors', ['base'])
cacheHierarchy = inc.cache.Cache('hierarchy', ['base'])
cacheDirectParents = inc.cache.Cache('directParents', ['base'])

# load exclusion file(s)
EXCLUDED_COLHEADERS = set()
with open(os.path.join(config.ASSET_PATH, 'excluded_colheaders.csv'), 'r') as f:
    for line in f:
        if not line.startswith('#'):
            EXCLUDED_COLHEADERS.add(line.strip())

EXCLUDED_CLASSES = set()
with open(os.path.join(config.ASSET_PATH, 'excluded_classes.csv'), 'r') as f:
    for line in f:
        if not line.startswith('#'):
            EXCLUDED_CLASSES.add(line.strip())
EXCLUDED_CLASSES_FORMATTED = ', '.join('<{}>'.format(i) for i in EXCLUDED_CLASSES)


async def get_ancestors_for_lst(entities):

    """
    Get the direct types and all their parents
    aka simulate a reasoner and get all classes of the given entities
    """

    res = await runQuerySingleKey(cacheAncestors, entities, f"""
      SELECT ?base ?type
      WHERE {{

        VALUES ?base {{ %s }} .
        ?base rdf:type ?type .
        FILTER( ?type NOT IN ({ EXCLUDED_CLASSES_FORMATTED }) ) # exclude Thing, Agent and redirects
        FILTER STRSTARTS(str(?type),"{config.SEMANTIC_TYPES_ONTO}")

      }}
      LIMIT { config.RESULTS_LIMIT }
    """,printIt=True)

    return res


async def get_hierarchy_for_lst(entities):
    """
    get the hierarchy for the given entities
    """

    res = await runQuerySingleKey(cacheHierarchy, entities, f"""
      SELECT DISTINCT ?base ?parent
      WHERE {{

        VALUES ?base {{ %s }} .
        ?base rdfs:subClassOf/rdfs:subClassOf* ?parent .
        FILTER( ?parent NOT IN ({ EXCLUDED_CLASSES_FORMATTED }) ) # exclude Thing, Agent and redirects
        FILTER STRSTARTS(str(?parent),"{config.SEMANTIC_TYPES_ONTO}")

      }}
      LIMIT { config.RESULTS_LIMIT }
    """)

    return res


async def get_direct_types_for_lst(entities):
    """
    get direct types (rdf:type & rdfs:subClassOf) for the given entities
    """

    res = await runQuerySingleKey(cacheDirectParents, entities, f"""
      SELECT ?base ?type
      WHERE {{

        VALUES ?base {{ %s }} .
        {{ ?base rdf:type ?type. }} #  direct parent in case of entity mention
        UNION
        {{ ?base rdfs:subClassOf ?type .}} # direct parent in case of class
        FILTER( ?type NOT IN ({ EXCLUDED_CLASSES_FORMATTED }) ) # exclude Thing, Agent and redirects
        FILTER STRSTARTS(str(?type),"{config.SEMANTIC_TYPES_ONTO}")

      }}
      LIMIT { config.RESULTS_LIMIT }
    """)

    return res
