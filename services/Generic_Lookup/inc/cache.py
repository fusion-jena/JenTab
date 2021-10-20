import json
import os
import sqlite3
import config

CACHE_DISABLED = os.environ.get('DISABLE_CACHE', False)


class Cache:
    """generic SQLite3 based cache"""

    def __init__(self, name, keys):

        # check keys
        if any(not k.isalnum() for k in keys):
            raise Exception('Keys can only contain alphanumeric characters')

        # memorize inputs
        self._name = name
        self._keys = keys

        # path to sqlite3 db file
        self._dbpath = os.path.join(config.CACHE_PATH, '{}.db3'.format(name))

        # open sqlite connection
        self._conn = sqlite3.connect(self._dbpath)
        self._db = self._conn.cursor()

        # make sure we have our db schema
        # column definition for keys
        cols = ['{} TEXT NOT NULL,'.format(k) for k in keys]
        # create table
        self._db.execute("""
          CREATE TABLE IF NOT EXISTS cache (
            {}
            payload TEXT DEFAULT NULL,
            PRIMARY KEY( {} )
          )
        """.format(' '.join(cols), ','.join(keys)))

        # prepare queries
        self._querySelect = """
          SELECT payload
          FROM cache
          WHERE {}
        """.strip().format(' AND '.join(['{}=:{}'.format(k, k) for k in self._keys]))

        self._queryInsert = """
          INSERT OR REPLACE INTO cache ({}, payload)
          VALUES ( {}, :payload )
        """.format(
            ','.join(self._keys),
            ','.join([':{}'.format(k) for k in self._keys])
        ).strip()

    def get(self, needle):
        """retrieve the payload for the keys given in needle"""

        # is caching enabled?
        if CACHE_DISABLED:
            return None

        # check the input
        if not isinstance(needle, dict):
            raise Exception('Invalid input type provided')
        if any(k not in needle for k in self._keys):
            raise Exception('Missing key in needle')

        # query the db for the payload
        self._db.execute(self._querySelect, needle)
        payload = self._db.fetchone()

        # parse the result before returning
        if payload:
            return json.loads(payload[0])
        else:
            return None

    def getMany(self, needles):
        """retrieve the payload for the keys given in needle"""

        # is caching enabled?
        if CACHE_DISABLED:
            return {'hits': [], 'misses': needles}

        # check the input
        if not isinstance(needles, list):
            raise Exception('Invalid input type provided')
        if any(not isinstance(el, dict) for el in needles):
            raise Exception('Invalid inner input type provided')
        if any(any(k not in needle for k in self._keys) for needle in needles):
            raise Exception('Missing key in needle')

        # run queries for all needles
        result = {'hits': [], 'misses': []}
        for needle in needles:

            # query the db for the payload
            self._db.execute(self._querySelect, needle)
            payload = self._db.fetchone()

            if payload:
                result['hits'].append({'key': needle, 'val': json.loads(payload[0])})
            else:
                result['misses'].append(needle)

        # done
        return result

    def set(self, needle, payload):
        """store the payload in the database"""

        # is caching enabled?
        if CACHE_DISABLED:
            return None

        # check the input
        if not isinstance(needle, dict):
            raise Exception('Invalid input type provided')
        if any(k not in needle for k in self._keys):
            raise Exception('Missing key in needle')

        # store in db
        self._db.execute(self._queryInsert, {**needle, 'payload': json.dumps(payload)})

    def setMany(self, items):
        """store the payloads in the database"""

        # is caching enabled?
        if CACHE_DISABLED:
            return None

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
        params = [{**item['key'], 'payload': json.dumps(item['val'])} for item in items]
        self._db.executemany(self._queryInsert, params)

    def __del__(self):
        """cleanup after obejct destruction"""
        self._conn.close()

    def __exit__(self, exc_type, exc_value, traceback):
        """cleanup after obejct destruction"""
        return self.__del__()
