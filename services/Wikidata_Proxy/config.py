import os

##### Lookup API Config.
Target_Ontology = "http://wikidata.org/entity/"
MaxHits = 50  # up to 50 according to https://www.wikidata.org/w/api.php?action=help&modules=wbsearchentities
Default_Lang = 'en'

# API URL
LOOKUP_API = "https://www.wikidata.org/w/api.php"

##### Endpoint API config.
# shorten all URIs returned
SHORTEN_URIS = True

# endpoint to query
wikidata_SPARQL_ENDPOINT = 'https://query.wikidata.org/sparql'

# endpoint for cache server
# None for local, SQlite-based cache
CACHE_ENDPOINT = None #'https://jentab-01.fmi.uni-jena.de/cache'
# credentials
CACHE_USERNAME = 'YourCacheUserName'
CACHE_PASSWORD = 'YourCachePassword'

# prefix for caching
# only used for endpoint
CACHE_PREFIX = 'wd_'

##### Shared config ...
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
    CACHE_PATH = os.path.abspath(os.path.join(CUR_PATH, '..', '..', 'assets', 'data', 'cache', 'Wikidata_Proxy'))
    ASSET_PATH = os.path.abspath(os.path.join(CUR_PATH, '..', '..', 'assets', 'Wikidata_Proxy'))

# make sure all paths exist
if not os.path.exists(CACHE_PATH):
    os.makedirs(CACHE_PATH)
