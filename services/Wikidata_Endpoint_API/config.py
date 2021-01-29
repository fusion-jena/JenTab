import os

# shorten all URIs returned
SHORTEN_URIS = True

# endpoint to query
wikidata_SPARQL_ENDPOINT = 'https://query.wikidata.org/sparql'

# maximum requests in parallel
# prevents IP-bans from Wikidata
MAX_PARALLEL_REQUESTS = int(os.environ.get('MAX_PARALLEL_REQUESTS', 5))

# default back-off time on 429 in case server does not give any
# time in seconds
DEFAULT_DELAY = int(os.environ.get('DEFAULT_DELAY', 10))

# maximum number of retries, if we are not at fault
MAX_RETRIES = int(os.environ.get('MAX_RETRIES', 5))

# paths
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
if os.environ.get('DOCKERIZED', False):
    CACHE_PATH = os.path.join(CUR_PATH, 'cache')
    ASSET_PATH = os.path.join(CUR_PATH, 'assets')
else:
    CACHE_PATH = os.path.abspath(os.path.join(CUR_PATH, '..', '..', 'assets', 'data', 'cache', 'Wikidata_Endpoint'))
    ASSET_PATH = os.path.abspath(os.path.join(CUR_PATH, '..', '..', 'assets', 'Wikidata_Endpoint'))

# make sure all paths exist
if not os.path.exists(CACHE_PATH):
    os.makedirs(CACHE_PATH)
