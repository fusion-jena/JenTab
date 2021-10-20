import aiohttp
import asyncio
import inc.cache
import config
import util_log

# global connection pool; will be initialized on first request
pool = None
# backoff event; used to rate limit on error
backoff = None
# cache of results
cache = inc.cache.Cache('terms', ['term'])

# terms we dont want to run
INVALID_TERMS = set(["", "nan"])


async def lookup(terms, lang=config.Default_Lang):
    """
    run DBpedia lookups for the requested terms
    """

    # only consider unique hits
    terms = list(set(terms))

    # check, if there is something in the cache
    cached = await cache.getMany([{'term': term} for term in terms])

    # init res if 'hits'
    res = {}
    for r in cached['hits']:
        res[r['key']['term']] = r['val']

    miss_res = {}
    # fire real requests if we have any misses
    if cached['misses']:
        # run lookups for all terms in parallel
        terms = [t['term'] for t in cached['misses']]
        reqs = [lookup_single(term, lang, skipCache=True) for term in terms]
        resp = await asyncio.gather(*reqs)
        # assemble result
        for r in resp:
            miss_res = {**miss_res, **r}

    # done (merge res from the two cases)
    res = {**res, **miss_res}

    return res


async def lookup_single(term, lang=config.Default_Lang, retriesLeft=config.MAX_RETRIES, skipCache=False):
    if config.USE_LOOKUP_SERVICE:
        res = await dbpedia_lookup_single(term, lang, retriesLeft, skipCache)
        # if not res[term]:  # empty results by dbpedia lookup api re-try with spotlight API
        #     res = await spotlight_lookup_single(term, lang, retriesLeft, skipCache)
        #     if res[term]:
        #         util_log.info("spotlight found: ", term)
        return res
    else:
        return await spotlight_lookup_single(term, lang, retriesLeft, skipCache)


async def spotlight_lookup_single(term, lang=config.Default_Lang, retriesLeft=config.MAX_RETRIES, skipCache=False):
    # TODO: not reliable, git rid of it.
    """
    run a single spotlight lookup
    """

    # check, if there is something in the cache
    if not skipCache:
        cached = await cache.get({'term': term})
        if cached is not None:
            return {term: cached}

    # we may be in backoff-mode
    global backoff
    if backoff:
        await backoff.wait()

    # if we have no more retries left, give up
    if retriesLeft <= 0:
        raise FailAfterRetries('Giving up on query after multiple retries. Query:\n{}'.format(statement))

    # make sure pool is initialized
    global pool
    if not pool:
        pool = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=config.MAX_PARALLEL_REQUESTS),
            trust_env=True
        )

    # prepare results
    res = {
        term: []
    }

    # short-circuit some (invalid) requests
    if (term in INVALID_TERMS) or term is None:
        return res

    # run the query
    params = {
        'text': term,
    }
    async with pool.get(config.SPOTLIGHT_LOOKUP_API, params=params, headers={"Accept": "application/json"}) as resp:

        # back of, if asked to
        if resp.status == 500:  # Too Many Requests

            # get the delay timer
            delay = resp.headers['Retry-After'] if ('Retry-After' in resp.headers) else config.DEFAULT_DELAY
            print(f"delaying for .... {delay}")
            # reduce the load by delaying the execution
            # TODO we should actually pause the pool
            localBackoff = asyncio.Event()
            backoff = localBackoff
            await asyncio.sleep(delay)
            localBackoff.set()

            # retry
            res = await spotlight_lookup_single(term, lang, retriesLeft - 1)
            return res

        # parse results
        results = (await resp.json())['annotation']

        # no results
        if 'surfaceForm' not in results:
            await cache.set({'term': term}, [])
            return res

        # extract results
        resource = results['surfaceForm']['resource']  # single entry is retrieved each time

        # get elements
        uri = 'http://dbpedia.org/resource/' + resource['@uri']
        labels = [resource['@label']]  # labels should be a list  for the rest of JenTab design

        # result entry
        res[term].append({'uri': uri, 'labels': labels})

    # add to cache
    await cache.set({'term': term}, res[term])

    # done
    return res


async def dbpedia_lookup_single(term, lang=config.Default_Lang, retriesLeft=config.MAX_RETRIES, skipCache=False):
    """
    run a single DBpedia lookup
    """

    # check, if there is something in the cache
    if not skipCache:
        cached = await get({'term': term})
        if cached is not None:
            return {term: cached}

    # we may be in backoff-mode
    global backoff
    if backoff:
        await backoff.wait()

    # if we have no more retries left, give up
    if retriesLeft <= 0:
        raise FailAfterRetries('Giving up on query after multiple retries. Query:\n{}'.format(statement))

    # make sure pool is initialized
    global pool
    if not pool:
        pool = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=config.MAX_PARALLEL_REQUESTS),
            trust_env=True
        )

    # prepare results
    res = {
        term: []
    }

    # short-circuit some (invalid) requests
    if (term in INVALID_TERMS) or term is None:
        return res

    # run the query
    params = {
        'QueryString': term,
        'language': lang,
        'format': 'json',
        'maxhits': config.MaxHits,
    }

    async with pool.get(config.LOOKUP_API, params=params, headers={"Accept": "application/json"}) as resp:

        # back of, if asked to
        if resp.status == 500:  # Too Many Requests (Disconnects)

            # get the delay timer
            delay = resp.headers['Retry-After'] if ('Retry-After' in resp.headers) else config.DEFAULT_DELAY
            print(f"delaying for .... {delay}")
            # reduce the load by delaying the execution
            # TODO we should actually pause the pool
            localBackoff = asyncio.Event()
            backoff = localBackoff
            await asyncio.sleep(delay)
            localBackoff.set()

            # retry
            res = await lookup_single(term, lang, retriesLeft - 1)
            return res

        # parse results
        results = await resp.json()
        if term == 'Dick Ruhi':
            print(results)

        # no results
        if len(results['docs']) == 0:
            await cache.set({'term': term}, [])
            return res

        # extract results
        for i in range(min(len(results['docs']), config.MaxHits)):  # Results may be less than Max_Hits

            # get elements
            uri = results['docs'][i]['resource'][0]  # CEA, for some reason API return a list of single URI
            labels = []
            if 'label' in results['docs'][i]:
                labels.extend(results['docs'][i]['label'])
            if 'redirectlabel' in results['docs'][i]:  # include aliases as well
                labels.extend(results['docs'][i]['redirectlabel'])

            # result entry
            res[term].append({'uri': uri, 'labels': labels})

        # add to cache
        await cache.set({'term': term}, res[term])

        # done
        return res


class FailAfterRetries(Exception):
    pass
