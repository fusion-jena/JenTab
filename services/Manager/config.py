import os
import util_log

# current dataset
ROUND = 1
YEAR = 2020

# configure output format
OUTPUT_ADD_PREFIX = False  # should URLs include the URL prefix defined?
OUTPUT_2019_FORMAT = False  # use the old order of columns in CEA-output (col_id before row_id)?

# init logs
# util_log.init('load_table.log')
util_log.init()

# prefix of entity URLs; used to save some space when storing results in the DB
URL_PREFIX = 'http://www.wikidata.org/entity/'

# paths
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
if os.environ.get('DOCKERIZED', False):
    BASE_PATH = os.path.join(CUR_PATH, 'assets', str(YEAR), "Round {0}".format(ROUND))
    CACHE_PATH = os.path.join(CUR_PATH, 'cache')
else:
    BASE_PATH = os.path.abspath(os.path.join(CUR_PATH, '..', '..', 'assets', 'data', 'input', str(YEAR), "Round {0}".format(ROUND)))
    CACHE_PATH = os.path.abspath(os.path.join(CUR_PATH, '..', '..', 'assets', 'data', 'cache', 'Manager'))
TABLES_PATH = os.path.join(BASE_PATH, 'tables')
TARGETS_PATH = os.path.join(BASE_PATH, 'targets')
WORK_PATH = os.path.join(CACHE_PATH, str(YEAR), str(ROUND))
RESULT_PATH = os.path.join(WORK_PATH, 'results')
ERROR_PATH = os.path.join(WORK_PATH, 'errors')
ANALYSIS_PATH = os.path.join(WORK_PATH, 'analysis')
AUDIT_PATH = os.path.join(WORK_PATH, 'audit')

# make sure all paths exist
if not os.path.exists(RESULT_PATH):
    os.makedirs(RESULT_PATH)
if not os.path.exists(ERROR_PATH):
    os.makedirs(ERROR_PATH)
if not os.path.exists(ANALYSIS_PATH):
    os.makedirs(ANALYSIS_PATH)
if not os.path.exists(AUDIT_PATH):
    os.makedirs(AUDIT_PATH)
util_log.info("Result path set to {}".format(RESULT_PATH))
util_log.info("Error path set to {}".format(ERROR_PATH))

# basic auth
# note this is only activated by setting the proper environment variable
BASIC_AUTH_ENABLED = os.environ.get('USE_BASIC_AUTH', False)
USER_NAME = 'YourManagerUsername'
USER_PASSWORD = 'YourManagerPassword'

# enable analysis logging
ENABLE_ANALYSIS = 'gt' == YEAR
if ENABLE_ANALYSIS:
    util_log.info("Analysis path set to {}".format(ANALYSIS_PATH))

# enable audit logging
ENABLE_AUDIT = True

# which return files to store
# actual results will always be stored in database
STORE_ERRORS = True
STORE_ERRORS_ZIP = True
STORE_RESULT = False
STORE_RESULT_ZIP = False
