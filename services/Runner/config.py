from util import get_ip
import util_log
import os
import uuid

# local mode (0) or docker mode (1)
run_mode = 1 if os.environ.get('DOCKERIZED', False) else 0

# manager node address
manager_url = 'http://10.138.225.141:5100' #meggy
# manager_url = 'http://127.0.0.1:5100' #local
# manager_url = 'http://ipc772.inf-bb.uni-jena.de/jentab/' #change password to fusion2020a?

# identifier for this runner node
client_id = get_ip() + ' - ' + str(uuid.uuid4())

# init logs
util_log.init()

# paths
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
if os.environ.get('DOCKERIZED', False):
    CACHE_PATH = os.path.join(CUR_PATH, 'cache')
else:
    CACHE_PATH = os.path.abspath(os.path.join(CUR_PATH, '..', '..', 'assets', 'data', 'cache', 'Runner'))

# make sure all paths exist
if not os.path.exists(CACHE_PATH):
    os.makedirs(CACHE_PATH)
util_log.info("Cache path set to {}".format(CACHE_PATH))

# If a column is too long, use this value to batch processing it. Used in prepareData
BATCH_SIZE = 500

# basic auth
# needed to connect to the manager node
USER_NAME = 'jentab'
USER_PASSWORD = 'fusion2020'

# Handles partial results as errors
RASIE_ERROR_FOR_INCOMPLETE_TABLES = True