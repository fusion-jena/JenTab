import asyncio
import time
from .aggregate import aggregateByKeys, formatOutput
from .util import getWikiID
from .query import query, runQuerySingleKey
import inc.cache

# init caches
cacheProperty = inc.cache.Cache('property', ['subj', 'obj'])
cacheLabels = inc.cache.Cache('labels', ['base'])
cachePopularity = inc.cache.Cache('popularity', ['base'])


async def get_connection_for_lst(pairs):
    """resolve the type for multiple subs and objs"""

    # replace any prefix, if present
    for p in pairs:
        p['subj'] = getWikiID(p['subj'])
        p['obj'] = getWikiID(p['obj'])

    # hit the cache
    cached = cacheProperty.getMany(pairs)
    pairs = cached['misses']
    if not pairs:
        # we already know all items
        return formatOutput(cached['hits'])

    # create the value list
    valueList = ['(wd:{subj} wd:{obj})'.format(**pair) for pair in pairs]

    # prepare query
    statement = """
                SELECT DISTINCT ?subj ?obj ?prop WHERE {
                  VALUES ( ?subj ?obj ) { %s }
                  ?subj ?p ?obj .
                  ?p ^wikibase:directClaim ?pEntity .
                  ?pEntity wdt:P1647* ?prop .
                }""" % ' '.join(valueList)

    # run query
    raw = await query(statement)

    # parse into result
    aggregated = aggregateByKeys(raw, ['subj', 'obj'])

    # store into cache
    if aggregated:
        cacheProperty.setMany(aggregated)

    # prepare output
    return formatOutput(aggregated + cached['hits'], pairs)


async def filter_entities_by_classes(entities, classes):
    """Filters entities that satisfy the given classes either by P31 or P279"""

    # make sure we have no duplicates
    entities = map(getWikiID, entities)
    entities = list(set(entities))

    classes = map(getWikiID, classes)
    classes = list(set(classes))

    # create the value list
    e_valueList = ' '.join(['wd:{}'.format(e) for e in entities])
    c_valueList = ' '.join(['wd:{}'.format(c) for c in classes])

    # prepare query
    statement = """
                  SELECT DISTINCT ?e ?eLabel
                  WHERE {
                    {?e  wdt:P31  ?c .} #instanceOf
                    UNION
                    {
                      ?e  wdt:P31 ?class .
                      ?class wdt:P279 ?c . #subclassOf
                    }
                    UNION
                    {
                      ?e  wdt:P279 ?c . #subclassOf
                    }
                    VALUES ?c { %s } # okey classes (classes)
                    VALUES ?e { %s } # output from Wikidata_Lookup_API (entities)
                    SERVICE wikibase:label {bd:serviceParam wikibase:language "en".}
                  }
                  ORDER BY ?p
                """ % (c_valueList, e_valueList)

    # run query
    raw = await query(statement)

    return {'res': raw}  # raw is a list of e = URI and eLabel = KB label


async def get_labels_raw_lst(entities):
    """
    get all labels for the given entities and return the raw results as returned by the query
    """

    # replace any prefix, if present
    # and filter for unique values
    entities = map(getWikiID, entities)
    entities = list(set(entities))

    # try to hit the cache
    cached = cacheLabels.getMany([{'base': e} for e in entities])
    entities = cached['misses']
    if not entities:
        # we already know all items
        return formatOutput(cached['hits'])

    # create the value list
    valueList = ' '.join(['wd:{}'.format(el['base']) for el in entities])

    # prepare query
    statement = """
                SELECT ?base ?prop ?value ?datatype ?wikitype
                WHERE {
                  VALUES ?base { %s }
                  VALUES ?prop { rdfs:label skos:altLabel schema:description }
                  ?base ?prop ?value .
                  BIND( DATATYPE(?value) AS ?datatype )
                }
                """ % valueList

    # run query
    raw = await query(statement)

    # strip down the result a little
    for line in raw:
        line['datatype'] = line['datatype'].split('#', 1)[1]

    # parse into result
    aggregated = aggregateByKeys(raw, ['base'])

    # store into cache
    if aggregated:
        cacheLabels.setMany(aggregated)

    # prepare output
    return formatOutput(aggregated + cached['hits'], entities)


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
          [] wikibase:directClaim ?prop .
        }
        GROUP BY ?base
    """)
    return res
