import aiohttp
import asyncio
import copy
import json
import traceback
import config
from util.util import getWikiID
from .aggregate import aggregateByKeys, formatOutput

# global connection pool; will be initialized on first request
pool = None
# backoff event; used to rate limit on error
backoff = None


def init():
    """initialize the connection pool"""
    # make sure pool is initialized
    global pool
    if not pool:
        pool = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=config.MAX_PARALLEL_REQUESTS),
            raise_for_status=False,
            trust_env=True
        )


def flattenResult(resp):
    """flatten the SPARQL response structure"""
    result = []
    for entry in resp['results']['bindings']:
        parsedEntry = {}
        result.append(parsedEntry)
        for key in entry.keys():
            if config.SHORTEN_URIS and (entry[key]['type'] == 'uri'):
                parsedEntry[key] = getWikiID(entry[key]['value'])
            else:
                parsedEntry[key] = entry[key]['value']
    return result


async def query(statement, retriesLeft=config.MAX_RETRIES):
    """run the query against the endpoint"""
    # make sure our pool exists
    init()

    # we may be in backoff-mode
    global backoff
    if backoff:
        await backoff.wait()

    # if we have no more retries left, give up
    if retriesLeft <= 0:
        raise FailAfterRetries('Giving up on query after multiple retries. Query:\n{}'.format(statement))

    # run the query
    async with pool.post(
        config.wikidata_SPARQL_ENDPOINT,
        data={'query': statement},
        headers={
            "Accept": "application/json",
        }
    ) as resp:

        # successful response
        if resp.status == 200:

            # get the text content
            text = await resp.text()

            # raise an error, if wikidata raised one
            if '\njava.util.concurrent.TimeoutException\n\tat' in text:
                raise WDTimeoutError("Query failed in Wikidata with timeout.\n\n" + statement)

            # otherwise just return the result
            results = json.loads(text)
            return flattenResult(results)

        # error, but we will retry
        if (resp.status == 429) or (resp.status >= 500):

            # get the text content
            text = await resp.text()

            # raise an error, for timeouts and do not continue
            if '\njava.util.concurrent.TimeoutException\n\tat' in text:
                raise WDTimeoutError("Query failed in Wikidata with timeout.\n\n" + statement)

            # get the delay timer
            delay = int(resp.headers['Retry-After']) if ('Retry-After' in resp.headers) else config.DEFAULT_DELAY

            # reduce the load by delaying the execution
            # TODO we should actually pause the pool
            localBackoff = asyncio.Event()
            backoff = localBackoff
            await asyncio.sleep(delay)
            localBackoff.set()

            # retry
            res = await query(statement, retriesLeft - 1)
            return res

        # for anything else, raise the default error
        resp.raise_for_status()


class FailAfterRetries(Exception):
    pass


class WDTimeoutError(Exception):
    pass


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HELPER ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


async def runQuerySingleKey(cache, entities, stmt, max_entity=10000, printIt=False):
    """
    generic query / cache function for queries that have a single key
    """

    # replace any prefix, if present
    # and filter for unique values
    entities = map(getWikiID, entities)
    entities = list(set(entities))

    # try to hit the cache
    cached = await cache.getMany([{'base': e} for e in entities])
    entities = cached['misses']
    if not entities:
        # we already know all items
        return formatOutput(cached['hits'])

    # split entities into sets of the proper size
    chunks = [entities[i:i + max_entity] for i in range(0, len(entities), max_entity)]

    # issue requests for each part
    reqs = []
    for chunk in chunks:

        # format base entities
        valuelist = ' '.join(['wd:{}'.format(el['base']) for el in chunk])

        # start request
        statement = stmt % valuelist
        if printIt:
            print(statement)
        reqs.append(query(statement))

    # wait until all queries are finished
    resp = await asyncio.gather(*reqs)
    raw = []
    errors = []
    entities_noResponse = set()
    for i in range(len(resp)):

        # shortcut
        part = resp[i]

        # process the result
        if isinstance(part, Exception):
            # store the error message
            try:
                raise part
            except:
                errors.append(traceback.format_exc())
            # keep track of the entities, we dont have an answer for
            entities_noResponse.update(chunks[i])
        else:
            raw.extend(part)

    # strip down the result a little
    # set the "default" property namespace
    for line in raw:
        if 'wikitype' in line:
            line['wikitype'] = line['wikitype'].replace('http://wikiba.se/ontology#', '')
        if ('datatype' in raw[0]) and ('#' in line['datatype']):
            line['datatype'] = line['datatype'].split('#', 1)[1]

    # parse into result
    aggregated = aggregateByKeys(raw, ['base'])

    # get a list of missing entities
    resolved = set(item['base'] for item in raw)
    missed = [
        item['base'] for item in entities
        if (item['base'] not in resolved) and (item['base'] not in entities_noResponse)
    ]

    # store into cache
    if missed:
        await cache.setMany([{'key': {'base': entity}, 'val': []} for entity in missed])
    if aggregated:
        await cache.setMany(aggregated)

    # prepare output
    return formatOutput(aggregated + cached['hits'], entities, errors=errors)


async def runQueryMultiKey(cache, values, stmt, max_entity=None):
    """
    generic query / cache function for queries that have a multiple keys
    !!!only base-key can have multiple values - code is only partially ready for more!!!
    !!!currently only base (first value) will be used as key for return!!!
    """

    # replace any prefix, if present
    # and filter for unique values
    unqiue_values = {
        key: list(set(map(getWikiID, value)))
        for key, value in values.items()
    }

    # check values
    for key, value in values.items():
        if (key != 'base') and (len(value) > 1):
            raise Exception('Only base can have multiple values for now')
    if 'base' not in values:
        raise Exception('Could not find base attribute')

    # prepare a template object to use for cache access
    template = {}
    for key, value in values.items():
        if key != 'base':
            template[key] = value[0]

    # try to hit the cache
    needles = []
    for entity in values['base']:
        entry = copy.deepcopy(template)
        entry['base'] = entity
        needles.append(entry)
    cached = await cache.getMany(needles)
    entities = cached['misses']
    if not entities:
        # we already know all items
        return formatOutput(cached['hits'], keys=['base'])
    unqiue_values['base'] = [e['base'] for e in entities]

    # create the value list
    formated_values = {
        key: ' '.join([f"wd:{el}" for el in value])
        for key, value in values.items()
    }

    errors = []
    entities_noResponse = set()
    if max_entity:
        # maximum number of entities per query

        # split base-values into sets of the proper size
        bases = [unqiue_values['base'][i:i + max_entity] for i in range(0, len(unqiue_values['base']), max_entity)]

        # issue requests for each part
        reqs = []
        for base in bases:

            # format base entities
            formated_values['base'] = ' '.join([f"wd:{el}" for el in base])

            # start request
            statement = stmt % tuple(formated_values.values())
            reqs.append(query(statement))

        # wait until all queries are finished
        resp = await asyncio.gather(*reqs, return_exceptions=True)
        raw = []
        for i in range(len(resp)):

            # shortcut
            part = resp[i]

            # process the result
            if isinstance(part, Exception):
                # store the error message
                try:
                    raise part
                except:
                    errors.append(traceback.format_exc())
                # keep track of the entities, we dont have an answer for
                entities_noResponse.update(bases[i])
            else:
                raw.extend(part)

    else:
        # unlimited number of entities per query

        # prepare query
        statement = stmt % tuple(formated_values.values())

        # run query
        raw = await query(statement)

    # strip down the result a little
    # set the "default" property namespace
    for line in raw:
        if 'wikitype' in line:
            line['wikitype'] = line['wikitype'].replace('http://wikiba.se/ontology#', '')
        if ('datatype' in raw[0]) and ('#' in line['datatype']):
            line['datatype'] = line['datatype'].split('#', 1)[1]

    # parse into result
    aggregated = aggregateByKeys(raw, ['base'])
    for entry in aggregated:
        for k, v in template.items():
            entry['key'][k] = v

    # get a list of missing entities
    resolved = set(item['base'] for item in raw)
    missed = [
        item['base'] for item in entities
        if (item['base'] not in resolved) and (item['base'] not in entities_noResponse)
    ]

    # store into cache
    if missed:
        entries = []
        for enitity in missed:
            entry = copy.deepcopy(template)
            entry['base'] = enitity
            entries.append(entry)
        await cache.setMany([{'key': entry, 'val': []} for entry in entries])
    if aggregated:
        await cache.setMany(aggregated)

    # prepare output
    return formatOutput(aggregated + cached['hits'], musthaves=unqiue_values['base'], keys=['base'], errors=errors)
