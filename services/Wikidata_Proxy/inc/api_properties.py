import asyncio
import os
from typing import OrderedDict
from .query import query, runQuerySingleKey, runQueryMultiKey
import inc.cache
import config

# init all relevant caches
cacheLiteralsTop = inc.cache.Cache('literalstop', ['base'])
cacheLiteralsFull = inc.cache.Cache('literalsfull', ['base'])
cacheObjectsTop = inc.cache.Cache('objectstop', ['base'])
cacheObjectsFull = inc.cache.Cache('objectsfull', ['base'])
cacheReverseObjectTop = inc.cache.Cache('reverseobjectstop', ['base'])
cacheReverseObjectClassed = inc.cache.Cache('reverseobjectsclassed', ['base', 'class'])
cacheStrings = {}
cacheLabels = {}

# load exclusion files
EXCLUDED_CLASSES = set()
with open(os.path.join(config.ASSET_PATH, 'excluded_classes.csv'), 'r') as f:
    for line in f:
        if not line.startswith('#'):
            EXCLUDED_CLASSES.add(line.strip())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Literals ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


async def get_literals_topranked_for_lst(entities):
    """
    get all primary literal properties for the given entities
    primary properties are those with the highest rank per property
    see https://www.wikidata.org/wiki/Help:Ranking
    """

    res = await runQuerySingleKey(cacheLiteralsTop, entities, """
      SELECT *
      WHERE {
        hint:Query hint:optimizer "None".
        VALUES ?base { %s }
        ?base ?prop ?value .
        [] wikibase:directClaim ?prop .
        FILTER( ISLITERAL( ?value ) )
        ?prop ^wikibase:directClaim/wikibase:propertyType ?wikitype .
        FILTER( ?wikitype NOT IN ( wikibase:ExternalId, wikibase:CommonsMedia ) )
        BIND( DATATYPE(?value) AS ?datatype )
      }
    """)
    return res


async def get_literals_full_for_lst(entities):
    """
    get all literal properties for the given entities
    this will fetch all literals regardless of their rank
    see https://www.wikidata.org/wiki/Help:Ranking
    """

    res = await runQuerySingleKey(cacheLiteralsFull, entities, """
      SELECT ?base ?prop ?value ?datatype ?wikitype
      WHERE {
        hint:Query hint:optimizer "None".
        VALUES ?base { %s }
        ?base ?propP ?stmt .
        [] wikibase:claim ?propP .
        ?stmt ?prop ?value .
        [] wikibase:statementProperty ?prop .
        FILTER( ISLITERAL( ?value ) ) .
        ?prop ^wikibase:statementProperty/wikibase:propertyType ?wikitype .
        FILTER( ?wikitype NOT IN ( wikibase:ExternalId, wikibase:CommonsMedia ) )
        BIND( DATATYPE(?value) AS ?datatype )
      }
    """)
    return res

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Objects ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


async def get_objects_topranked_for_lst(entities):
    """
    get all primary object properties for the given entities
    primary properties are those with the highest rank per property
    see https://www.wikidata.org/wiki/Help:Ranking
    """

    res = await runQuerySingleKey(cacheObjectsTop, entities, """
      SELECT *
      WHERE {
        hint:Query hint:optimizer "None".
        VALUES ?base { %s }
        ?base ?prop ?value .
        FILTER( isIRI( ?value ) )
        ?prop ^wikibase:directClaim/wikibase:propertyType ?wikitype .
        FILTER( ?wikitype = wikibase:WikibaseItem )
        BIND( "IRI" AS ?datatype )
      }
    """)
    return res


async def get_objects_full_for_lst(entities):
    """
    get all object properties for the given entities
    this will fetch all literals regardless of their rank
    see https://www.wikidata.org/wiki/Help:Ranking
    """

    res = await runQuerySingleKey(cacheObjectsFull, entities, """
      SELECT ?base ?prop ?value ?datatype ?wikitype
      WHERE {
        hint:Query hint:optimizer "None".
        VALUES ?base { %s }
        ?base ?propP ?stmt .
        [] wikibase:claim ?propP .
        ?stmt ?prop ?value .
        FILTER( ISIRI( ?value ) ) .
        ?prop ^wikibase:statementProperty/wikibase:propertyType ?wikitype .
        FILTER( ?wikitype = wikibase:WikibaseItem )
        BIND( "IRI" AS ?datatype )
      }
    """)
    return res

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Reverse Objects ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


async def get_reverse_objects_topranked_for_lst(entities):
    """
    get pairs that point to the given entity as the primary property
    primary properties are those with the highest rank per property
    see https://www.wikidata.org/wiki/Help:Ranking
    """

    # some lookups just take too long, so we remove them here
    remEntities = set()
    for entity in ['Q2']:
        if entity in entities:
            entities.remove(entity)
            remEntities.add(entity)

    # short-circuit, if nothing is left
    if not entities:
        return {k: [] for k in remEntities}

    # run the query
    res = await runQuerySingleKey(cacheReverseObjectTop, entities, """
      SELECT ?base ?prop ?parent
      WHERE {
        hint:Query hint:optimizer "None".
        VALUES ?base { %s }
        ?parent ?prop ?base .
        [] wikibase:directClaim ?prop .
      }
    """, max_entity=100)

    # add the skipped entities again
    for k in remEntities:
        res[k] = []

    return res


async def get_reverse_objects_classed_for_lst(entities, klass):
    """
    get triples that point to the given entity as the target
    and whose subject is of the given class
    """

    # some klasses result in timeouts or are highly improbable, soe we remove them
    if klass in EXCLUDED_CLASSES:
        return {}

    # preserve the order of values in the dict,
    # so we can match them to placeholders in query
    values = OrderedDict()
    values['base'] = entities
    values['class'] = [klass]

    res = await runQueryMultiKey(cacheReverseObjectClassed, values, """
      SELECT ?base ?prop ?parent
      WHERE {
        # hint:Query hint:optimizer "None".
        VALUES ?base { %s }
        VALUES ?class { %s }
        ?parent (wdt:P31|wdt:P279) ?class .
        ?parent ?prop ?base .
        [] wikibase:directClaim ?prop .
      }
    """, max_entity=2)
    return res

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Strings ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


async def get_strings_for_lst(entities, lang='en'):
    """
    get all string properties for the given entities (labels, alias, description)
    primary properties are those with the highest rank per property
    see https://www.wikidata.org/wiki/Help:Ranking
    """

    # make sure there is a cache for this language
    if lang not in cacheStrings:
        cacheStrings[lang] = inc.cache.Cache('strings_' + lang, ['base'])

    res = await runQuerySingleKey(cacheStrings[lang], entities, """
      SELECT *
      WHERE {
        hint:Query hint:optimizer "None".
        VALUES ?base { %s }
        VALUES ?prop { rdfs:label skos:altLabel schema:description }
        ?base ?prop ?value .
        FILTER( LANG(?value) = "%s" )
        BIND( "Monolingualtext" AS ?wikitype )
        BIND( DATATYPE(?value) AS ?datatype )
      }
    """ % ('%s', lang))
    return res

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Labels ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


async def get_labels_for_lst(entities, lang='en'):
    """
    get the main labels for the given entities
    """

    # make sure there is a cache for this language
    if lang not in cacheLabels:
        cacheLabels[lang] = inc.cache.Cache('labels_' + lang, ['base'])

    res = await runQuerySingleKey(cacheLabels[lang], entities, """
      SELECT ?base ?l
      WHERE {
        VALUES ?base { %s }
        ?base rdfs:label|skos:altLabel ?l
        FILTER( LANG(?l) = '%s' )
      }
    """ % ('%s', lang), max_entity=5000)
    return res

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ All Properties ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


async def get_properties_topranked_for_lst(entities, lang='en'):
    """
    get all primary properties for the given entities no matter the type
    primary properties are those with the highest rank per property
    see https://www.wikidata.org/wiki/Help:Ranking
    """

    # get results for all sorts of properties
    reqs = [
        get_literals_topranked_for_lst(entities),
        get_objects_topranked_for_lst(entities),
        # get_strings_for_lst(entities, lang),  # values are already included in get_literals
    ]
    partials = await asyncio.gather(*reqs)

    # combine them into one object
    res = {}
    for partial in partials:
        for k in partial.keys():
            if k not in res:
                res[k] = []
            res[k] += partial[k]

    return res


async def get_properties_full_for_lst(entities, lang='en'):
    """
    get all properties for the given entities no matter the type
    this will fetch all properties regardless of their rank
    see https://www.wikidata.org/wiki/Help:Ranking
    """

    # get results for all sorts of properties
    reqs = [
        get_literals_full_for_lst(entities),
        get_objects_full_for_lst(entities),
        # get_strings_for_lst(entities, lang),  # values are already included in get_literals
    ]
    partials = await asyncio.gather(*reqs)

    # combine them into one object
    res = {}
    for partial in partials:
        for k in partial.keys():
            if k not in res:
                res[k] = []
            res[k] += partial[k]

    return res
