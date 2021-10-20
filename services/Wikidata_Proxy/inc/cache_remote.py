import os
import config
import aiohttp
import asyncio

CACHE_DISABLED = os.environ.get('DISABLE_CACHE', False)

# global connection pool; will be initialized on first request
pool = None


def init():
    """initialize the connection pool"""
    # make sure pool is initialized
    global pool
    if not pool:
        pool = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=config.MAX_PARALLEL_REQUESTS),
            raise_for_status=False,
            trust_env=True,
            auth=aiohttp.BasicAuth( config.CACHE_USERNAME, config.CACHE_PASSWORD ),
        )


class Cache:
    """generic remote cache"""

    def __init__(self, name, keys):

        # check keys
        if any(not k.isalnum() for k in keys):
            raise Exception('Keys can only contain alphanumeric characters')

        # memorize inputs
        self._name = name
        self._keys = keys


    def buildKey( self, needle ):
        """connect all keys to a single one; uses a unique symbol to separate"""
        return '§'.join([needle[k] for k in self._keys])


    async def get(self, needle):
        """retrieve the payload for the keys given in needle"""

        # is caching enabled?
        if CACHE_DISABLED:
            return None

        # make sure pool exists
        init()

        # check the input
        if not isinstance(needle, dict):
            raise Exception('Invalid input type provided')
        if any(k not in needle for k in self._keys):
            raise Exception('Missing key in needle')

        # query the db for the payload
        async with pool.get(
            config.CACHE_ENDPOINT + '/' + config.CACHE_PREFIX + self._name,
            json=[self.buildKey(needle)],
            headers={
                "Accept": "application/json",
            }
        ) as resp:

            if resp.status == 200:
                # success
                raw = await resp.json()
                if (needle in raw) and raw[needle]:
                    return raw[needle]
                else:
                    return None
            else:
                # fail
                raise Exception( await resp.text() )


    async def getMany(self, needles, max_entity=100000):
        """retrieve the payload for the keys given in needle"""

        # is caching enabled?
        if CACHE_DISABLED:
            return {'hits': [], 'misses': needles}

        # make sure pool exists
        init()

        # check the input
        if not isinstance(needles, list):
            raise Exception('Invalid input type provided')
        if any(not isinstance(el, dict) for el in needles):
            raise Exception('Invalid inner input type provided')
        if any(any(k not in needle for k in self._keys) for needle in needles):
            raise Exception('Missing key in needle')

        # split into smaller queries if too large
        chunks = [needles[i:i + max_entity] for i in range(0, len(needles), max_entity)]

        # run queries for all needles
        result = {'hits': [], 'misses': []}
        for chunk in chunks:

            async with pool.get(
                config.CACHE_ENDPOINT + '/' + config.CACHE_PREFIX + self._name,
                json=[self.buildKey(needle) for needle in chunk],
                headers={
                    "Accept": "application/json",
                    # https://github.com/aio-libs/aiohttp/issues/850#issuecomment-471663047
                    "Connection": "close",
                }
            ) as resp:

                if resp.status == 200:
                    # success
                    raw = await resp.json()
                    for n in chunk:
                        needle = self.buildKey(n)
                        if (needle in raw) and (raw[needle] is not None):
                            result['hits'].append({'key': n, 'val': raw[needle]})
                        else:
                            result['misses'].append(n)
                else:
                    # fail
                    raise Exception( await resp.text() )

        # done
        return result


    async def set(self, needle, payload):
        """store the payload in the database"""

        # is caching enabled?
        if CACHE_DISABLED:
            return None

        # make sure pool exists
        init()

        # check the input
        if not isinstance(needle, dict):
            raise Exception('Invalid input type provided')
        if any(k not in needle for k in self._keys):
            raise Exception('Missing key in needle')

        # store in db
        async with pool.put(
            config.CACHE_ENDPOINT + '/' + config.CACHE_PREFIX + self._name,
            json=[{ 'key': self.buildKey(needle), 'value': payload }],
            headers={
                "Accept": "application/json",
            }
        ) as resp:

            if resp.status == 200:
                # success
                return True
            else:
                # fail
                raise Exception( await resp.text() )


    async def setMany(self, items):
        """store the payloads in the database"""

        # is caching enabled?
        if CACHE_DISABLED:
            return None

        # make sure pool exists
        init()

        # check the input
        if not isinstance(items, list):
            raise Exception('Invalid input type provided')
        for item in items:
            if 'key' not in item:
                raise Exception('Missing key in item')
            if 'val' not in item:
                raise Exception('Missing value in item')
            if any(k not in item['key'] for k in self._keys):
                raise Exception('Missing field in key')

        # store in db
        async with pool.put(
            config.CACHE_ENDPOINT + '/' + config.CACHE_PREFIX + self._name,
            json=[{'key': self.buildKey(item['key']), 'value': item['val']} for item in items],
            headers={
                "Accept": "application/json",
            }
        ) as resp:

            if resp.status == 200:
                # success
                return True
            else:
                # fail
                raise Exception( await resp.text() )
