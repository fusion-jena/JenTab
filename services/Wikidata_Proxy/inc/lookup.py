import json
import aiohttp
import asyncio
import os
import urllib
import inc.cache
import config


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
    run Wikidata lookups for the requested terms
    """

    # only consider unique hits
    terms = list(set(terms))

    # check, if there is something in the cache
    cached = await cache.getMany([{'term': term} for term in terms])

    # set initial res for those keys in hits
    res = {}
    if cached['hits']:
        for r in cached['hits']:
            res[r['key']['term']] = r['val']

        if not cached['misses']:
            return res

    # run lookups for all terms in parallel
    terms = [t['term'] for t in cached['misses']]
    reqs = [lookup_single(term, lang, skipCache=True) for term in terms]
    resp = await asyncio.gather(*reqs)

    # update res with what comes from re-hit lookup with missed cache.
    for r in resp:
        res.update({**res, **r})

    # done
    return res


async def lookup_single(term, lang=config.Default_Lang, retriesLeft=config.MAX_RETRIES, skipCache=False):
    """
    run a single Wikidata lookup
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
        'action': 'wbsearchentities',
        'search': term,
        'language': lang,
        'format': 'json',
        'limit': config.MaxHits,
    }
    async with pool.get(config.LOOKUP_API, params=params, headers={"Accept": "application/json"}) as resp:

        # back of, if asked to
        if resp.status == 429:  # Too Many Requests

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

        # no results
        if len(results['search']) == 0:
            await cache.set({'term': term}, [])
            return res

        # extract results
        for i in range(min(len(results['search']), config.MaxHits)):  # Results may be less than Max_Hits

            # get elements
            uri = results['search'][i]['concepturi']  # CEA
            labels = []
            if 'label' in results['search'][i]:
                labels.append(results['search'][i]['label'])
            if 'aliases' in results['search'][i]:
                labels.extend(results['search'][i]['aliases'])

            # result entry
            res[term].append({'uri': uri, 'labels': labels})

        # add to cache
        await cache.set({'term': term}, res[term])

        # done
        return res


class FailAfterRetries(Exception):
    pass
