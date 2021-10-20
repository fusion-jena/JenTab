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
ex_cls = ', '.join('<{}>'.format(i) for i in EXCLUDED_CLASSES)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Literals ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


async def get_labels_for_lst(entities, lang='en'):
    """
    get the main labels for the given entities
    """

    # make sure there is a cache for this language
    if lang not in cacheLabels:
        cacheLabels[lang] = inc.cache.Cache('labels_' + lang, ['base'])

    try:
        res = await runQuerySingleKey(cacheLabels[lang], entities, """
          SELECT ?base ?l
          WHERE {
            VALUES ?base { %s }
            ?base rdfs:label|skos:altLabel ?l
            FILTER( LANG(?l) = '"""+lang+"""' )         
          }
          LIMIT """ + str(config.RESULTS_LIMIT) + """
        """)
        return res
    except Exception as ex:
        print(ex)


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
        VALUES ?base { %s }
        VALUES ?class { %s }
        ?parent rdf:type ?class .
        ?parent ?prop ?base .        
        FILTER( ?prop NOT IN (""" + ex_cls + """) ) # exclude wikilinks and redirects       
      }
      LIMIT """ + str(config.RESULTS_LIMIT) + """ 
    """, max_entity=5)
    return res


async def get_reverse_objects_topranked_for_lst(entities):
    """
    get pairs that point to the given entity as the primary property
    primary properties are those with the highest rank per property

    """
    # run the query
    res = await runQuerySingleKey(cacheReverseObjectTop, entities, """
      SELECT ?base ?prop ?parent
      WHERE {        
        VALUES ?base { %s }
        ?parent ?prop ?base .         
        FILTER( ?prop NOT IN (""" + ex_cls + """) ) # exclude wikilinks and redirects
        }
        LIMIT """ + str(config.RESULTS_LIMIT) + """
    """)

    return res


async def get_properties_full_for_lst(entities, lang='en'):
    """
    get all properties for the given entities no matter the type
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


async def get_objects_full_for_lst(entities):
    """
    get all object properties for the given entities
    """

    res = await runQuerySingleKey(cacheObjectsFull, entities, """
      SELECT ?base ?prop ?value ?datatype
      WHERE {
        VALUES ?base { %s }
        ?base ?prop ?value.
        FILTER( ISIRI( ?value ) ) .
        BIND( "IRI" AS ?datatype )
        FILTER( ?prop NOT IN (""" + ex_cls + """) ) # exclude wikilinks and redirects
        FILTER (CONTAINS(str(?prop), "http://dbpedia.org/")) # include props that are in DBpedia only         
      }
      LIMIT """ + str(config.RESULTS_LIMIT) + """
    """)
    return res


async def get_literals_full_for_lst(entities):
    """
    get all literal properties for the given entities
    this will fetch all literals regardless of their rank
    apply some filters and processing on the retrieved datatypes
    returned datatypes = ['string', 'quantity', 'date', 'anyURI', 'decimal']
    """

    res = await runQuerySingleKey(cacheLiteralsFull, entities, """
      SELECT ?base ?prop ?value ?datatype
      WHERE {
            VALUES ?base { %s }
            ?base ?prop ?value .
            FILTER( ISLITERAL( ?value ) ) .
            BIND( DATATYPE(?value) AS ?datatype )
            FILTER (!CONTAINS(str(?datatype), "")) # exclude empty datatypes
            FILTER (CONTAINS(str(?prop), "http://dbpedia.org/")) # include props that are in DBpedia only
       }
       LIMIT """ + str(config.RESULTS_LIMIT) + """ 
       """)

    # get the useful part of the datatype only ...
    for k, v in res.items():
        for prop_dict in v:
            # any prop with this uri handle it like "quantity"
            if prop_dict['datatype'].find('http://dbpedia.org/datatype') > -1:
                prop_dict['datatype'] = 'quantity'
            else:
                # other cases are formatted like URI + # + meaningful datatype, so, we get the meaningful type only
                # full list of DBpedia datatypes: http://mappings.dbpedia.org/index.php/DBpedia_Datatypes
                tmp = prop_dict['datatype'].split('#')
                datatype = tmp[len(tmp) - 1]
                datatype = datatype.lower()

                # includes (negativeInteger, nonNegativeInteger, nonPositiveInteger, positiveInteger)
                if datatype.find('integer') > -1 \
                        or datatype.find('float') > -1 \
                        or datatype.find('double') > -1:
                    datatype = 'decimal'

                # includes (langString, string)
                elif datatype.find('string') > -1:
                    datatype = 'string'

                # includes (date, time, datetime)
                elif datatype in ['date', 'time', 'datetime']:
                    datatype = 'date'

                # anyURI
                elif datatype.find('anyuri') > -1:
                    datatype = 'anyURI'

                else:
                    datatype = 'quantity'

                prop_dict['datatype'] = datatype
    return res
