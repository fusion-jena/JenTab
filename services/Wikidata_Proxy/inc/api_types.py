import os
from .query import runQuerySingleKey
import inc.cache
import config

# init caches
cacheTypes = inc.cache.Cache('types', ['base'])
cacheAncestors = inc.cache.Cache('ancestors', ['base'])
cacheHierarchy = inc.cache.Cache('hierarchy', ['base'])
cacheDirectParents = inc.cache.Cache('directParents', ['base'])
cacheInstances = inc.cache.Cache('instances', ['base'])

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


async def get_type_lst(entities):
    """
    Get most specific type for a given entity mention P31 in Wikidata
    """

    res = await runQuerySingleKey(cacheTypes, entities, """
      SELECT ?base ?type ?typeLabel
      WHERE {
        VALUES ?base { %s } .
        ?base wdt:P31/wdt:P279* ?type .
        SERVICE wikibase:label {bd:serviceParam wikibase:language "en".}
      }
    """)
    return res


async def get_ancestors_for_lst(entities):

    """
    Get the direct types and all their parents
    aka simulate a reasoner and get all classes of the given entities
    """
    # P31
    # res = await runQuerySingleKey(cacheAncestors, entities, """
    #      SELECT ?base ?type
    #      WHERE {
    #        VALUES ?base { %s } .
    #        ?base wdt:P31 ?type .
    #      }
    #     """)
    # multiple hops
    # res = await runQuerySingleKey(cacheAncestors, entities, """
    #  SELECT ?base ?type
    #  WHERE {
    #    VALUES ?base { %s } .
    #    ?base wdt:P31/wdt:P279* ?type .
    #  }
    # """)
    # disabled for now: ?base (wdt:P31/wdt:P279*)|wdt:P279+ ?type .

    # 2 hops including if entity == class
    res = await runQuerySingleKey(cacheAncestors, entities, """
      SELECT DISTINCT ?base ?type
      WHERE
      {
        {
          VALUES ?base { %s } .
          { ?base wdt:P31 ?type. } #  direct instanceOf P31 (most fine-grained type)
          UNION
          {
            ?base wdt:P31 ?t.
            ?t wdt:P279 ?type .  # parent of the instanceOf P279 (next fine-grained type)
          }
          UNION
          { ?base wdt:P279 ?type .} # if base is a class then retrieves its parent directly P279
        }
      }
    """,printIt=False)
    # filtered result placeholder
    f_res = {}
    # get rid of excludedClasses
    [f_res.update({base: [t for t in types if t['type'] not in EXCLUDED_CLASSES]}) for base, types in res.items()]
    return f_res


async def get_hierarchy_for_lst(entities):
    """
    get the hierarchy for the given entities
    """

    res = await runQuerySingleKey(cacheHierarchy, entities, """
      SELECT ?base ?parent
      WHERE {
        VALUES ?base { %s } .
        ?base wdt:P279 ?parent .
      }
    """)

    # filtered result placeholder
    f_res = {}
    # get rid of excludedClasses
    [f_res.update({base: [t for t in types if t['parent'] not in EXCLUDED_CLASSES]}) for base, types in res.items()]
    return f_res


async def get_direct_types_for_lst(entities):
    """
    get direct types (P31 & P279) for the given entities
    entities could be mentions (P31 is the direct parent) or classes (P279 is the direct parent)
    """

    res = await runQuerySingleKey(cacheDirectParents, entities, """
      SELECT ?base ?type
      WHERE {
        VALUES ?base { %s } .
        { ?base wdt:P31 ?type. } #  direct parent in case of entity mention
        UNION
        { ?base wdt:P279 ?type .} # direct parent in case of class
      }
    """)

    # filtered result placeholder
    f_res = {}
    # get rid of excludedClasses
    [f_res.update({base: [t for t in types if t['type'] not in EXCLUDED_CLASSES]}) for base, types in res.items()]
    return f_res


async def get_children_for_lst(entities):
    """
    get direct instances (P31 & P279) for the given entities
    """

    # some lookups just take too long, so we remove them here
    remEntities = set()
    for entity in entities:
        if entity in EXCLUDED_COLHEADERS:
            entities.remove(entity)
            remEntities.add(entity)

    # short-circuit, if nothing is left
    if not entities:
        return {k: [] for k in remEntities}

    # run the query
    res = await runQuerySingleKey(cacheInstances, entities, """
      SELECT ?base ?child
      WHERE {
        VALUES ?base { %s } .
        { ?child p:P31/ps:P31 ?base . }
        UNION
        { ?child p:P279/ps:P279 ?base . }
      }
    """, max_entity=5 )

    # add the skipped entities again
    for k in remEntities:
        res[k] = []

    return res
