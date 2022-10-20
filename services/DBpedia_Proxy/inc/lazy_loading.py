import os
import aiohttp
import asyncio
import copy
import json
import traceback
import config
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
                parsedEntry[key] = entry[key]['value']
            else:
                parsedEntry[key] = entry[key]['value']
    return result




async def get_all_taxons():
    init()
    offest = 0
    while True:

        # run the query
        query = "SELECT DISTINCT *  " \
                "WHERE {" \
                "VALUES ?parent { dbo:Bird dbo:Plant dbo:Mammal dbo:Fish  dbo:Bacteria dbo:Insect } ." \
                "{ ?species rdf:type ?parent .  } " \
                "}" \
                "OFFSET " + str(offest) + " LIMIT  10000"

        async with pool.post(
                config.SPARQL_ENDPOINT,
                data={'query': query},
                headers={
                    "Accept": "application/json",
                }
        ) as resp:

            # successful response
            if resp.status == 200:

                # get the text content
                text = await resp.text()

                # raise an error, if endpoint raised one
                if '\njava.util.concurrent.TimeoutException\n\tat' in text:
                    raise WDTimeoutError("Query failed in Wikidata with timeout.\n\n" + query)

                # otherwise just return the result
                results = json.loads(text)
                global_results = flattenResult(results)
                print(f'Offset: {offest} has {len(global_results)}')

        if not global_results:
            break
        else:
            with open(os.path.join(os.path.realpath('.'), 'query_taxon.csv'), 'a', encoding='utf-8') as file:
                file.write('\n'.join([r['species'] for r in global_results]))

        offest += 10000 # increase by page size (10K)

async def get_all_chemicals():
    init()
    offest = 0
    while True:

        # run the query
        query = "SELECT DISTINCT *  " \
                "WHERE {" \
                "VALUES ?parent { dbo:ChemicalCompound dbo:ChemicalElement dbo:ChemicalSubstance} ." \
                "{ ?element  rdf:type ?parent .  } " \
                "}" \
                "OFFSET " + str(offest) + " LIMIT  10000"

        async with pool.post(
                config.SPARQL_ENDPOINT,
                data={'query': query},
                headers={
                    "Accept": "application/json",
                }
        ) as resp:

            # successful response
            if resp.status == 200:

                # get the text content
                text = await resp.text()

                # raise an error, if endpoint raised one
                if '\njava.util.concurrent.TimeoutException\n\tat' in text:
                    raise WDTimeoutError("Query failed in Wikidata with timeout.\n\n" + query)

                # otherwise just return the result
                results = json.loads(text)
                global_results = flattenResult(results)
                print(f'Offset: {offest} has {len(global_results)}')

        if not global_results:
            break
        else:
            with open(os.path.join(os.path.realpath('.'), 'query_chemical_elements.csv'), 'a', encoding='utf-8') as file:
                file.write('\n'.join([r['element'] for r in global_results]))

        offest += 10000 # increase by page size (10K)

async def get_all_years():
    init()
    offest = 0
    while True:

        # run the query
        query = "SELECT DISTINCT *  " \
                "WHERE {" \
                "VALUES ?parent { dbo:Year } ." \
                "{ ?year  rdf:type ?parent .  } " \
                "}" \
                "OFFSET " + str(offest) + " LIMIT  10000"

        async with pool.post(
                config.SPARQL_ENDPOINT,
                data={'query': query},
                headers={
                    "Accept": "application/json",
                }
        ) as resp:

            # successful response
            if resp.status == 200:

                # get the text content
                text = await resp.text()

                # raise an error, if endpoint raised one
                if '\njava.util.concurrent.TimeoutException\n\tat' in text:
                    raise WDTimeoutError("Query failed in Wikidata with timeout.\n\n" + query)

                # otherwise just return the result
                results = json.loads(text)
                global_results = flattenResult(results)
                print(f'Offset: {offest} has {len(global_results)}')

        if not global_results:
            break
        else:
            with open(os.path.join(os.path.realpath('.'), 'query_years.csv'), 'a', encoding='utf-8') as file:
                years = [r['year'].split('_')[0] for r in global_results if len(r['year'].split('_')) == 1]
                file.write('\n'.join(years))

        offest += 10000 # increase by page size (10K)

class FailAfterRetries(Exception):
    pass


class WDTimeoutError(Exception):
    pass