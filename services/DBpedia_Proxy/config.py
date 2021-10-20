import os

# SEMANTIC_TYPES_ONTO = "http://schema.org"
SEMANTIC_TYPES_ONTO = "http://dbpedia.org/ontology/"

# ~~~~~~~~~~~~~~~~~~ Lookup API ~~~~~~~~~~~~~~~~~~~~~~~~~~
Target_Ontology = "http://dbpedia.org/ontology/"
MaxHits = 10  # up to ? I don't know the exact number allowed by DBpedia.
Default_Lang = 'en'

# API URL
LOOKUP_API = "http://lookup.dbpedia.org/api/search/PrefixSearch"
# found in an old forum https://forum.dbpedia.org/t/new-dbpedia-lookup-application/607
# this replaces the old Lookup application?
# Project link https://github.com/dbpedia/dbpedia-lookup
# LOOKUP_API = "http://akswnc7.informatik.uni-leipzig.de/lookup/api/search"
SPOTLIGHT_LOOKUP_API = 'https://api.dbpedia-spotlight.org/en/candidates'

USE_LOOKUP_SERVICE = True  # False will use Spotlight...

# ~~~~~~~~~~~~~~~~~~~~~~~ Endpoint ~~~~~~~~~~~~~~~~~~~~
# shorten all URIs returned
SHORTEN_URIS = True

# endpoint to query
SPARQL_ENDPOINT = 'https://dbpedia.org/sparql'
# SPARQL_ENDPOINT = 'https://jentab-01.fmi.uni-jena.de/dbpedia'  # our local setup

# endpoint for cache server
# None for local, SQlite-based cache
CACHE_ENDPOINT = None
# CACHE_ENDPOINT = 'https://jentab-01.fmi.uni-jena.de/cache'
# credentials
CACHE_USERNAME = 'YourCacheUserName'
CACHE_PASSWORD = 'YourCachePassword'

# prefix for caching
# only used for endpoint
CACHE_PREFIX = 'dbp_'

# maximum requests in parallel https://wiki.dbpedia.org/public-sparql-endpoint
MAX_PARALLEL_REQUESTS = int(os.environ.get('MAX_PARALLEL_REQUESTS', 10))

# default back-off time for DBpedia ??
# time in seconds
DEFAULT_DELAY = int(os.environ.get('DEFAULT_DELAY', 10))

# maximum number of retries, if we are not at fault
MAX_RETRIES = int(os.environ.get('MAX_RETRIES', 5))

# Max rows that could return https://wiki.dbpedia.org/public-sparql-endpoint
RESULTS_LIMIT = 10000

# paths
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
if os.environ.get('DOCKERIZED', False):
    CACHE_PATH = os.path.join(CUR_PATH, 'cache')
    ASSET_PATH = os.path.join(CUR_PATH, 'assets')
else:
    CACHE_PATH = os.path.abspath(os.path.join(CUR_PATH, '..', '..', 'assets', 'data', 'cache', 'DBpedia_Proxy'))
    ASSET_PATH = os.path.abspath(os.path.join(CUR_PATH, '..', '..', 'assets', 'DBpedia_Proxy'))

# make sure all paths exist
if not os.path.exists(CACHE_PATH):
    os.makedirs(CACHE_PATH)
