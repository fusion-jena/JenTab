import os
from os.path import join

# local mode (0) or docker mode (1)
run_mode = 1 if os.environ.get('DOCKERIZED', False) else 0

OBJ_COL = 'OBJECT'
LIT_COL = 'LITERAL'
MAX_TOKENS = 5  # Tokens inside cells to be checked individually


DBPEDIA = 1
WIKIDATA = 2
# TARGET_KG = DBPEDIA
TARGET_KG = WIKIDATA

Wikidata_Prefix = 'http://www.wikidata.org/entity/'  # Used to shorten the full mappingd URIs
Wikidata_Prop_Prefix = 'http://www.wikidata.org/prop/direct/'

# internal_storage_config
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
if os.environ.get('DOCKERIZED', False):
    BASE_PATH = os.path.join(CUR_PATH, 'cache')
else:
    BASE_PATH = os.path.abspath(os.path.join(CUR_PATH, '..', '..', 'assets', 'data', 'cache', 'Baseline_Approach'))

TABLE_RES_PATH = os.path.join(BASE_PATH, 'table_res_json')
if not os.path.exists(TABLE_RES_PATH):
    os.makedirs(TABLE_RES_PATH)

# log intermediate results for later analysis
# this is usually triggered externally when run with ground truth, so we can verify partial results
LOG_INTERMEDIATE_RESULTS = False

# log audit records
# this is usually triggered externally from Runner/Clients
AUDIT_ACTIVATED = True

# deduce object columns from target definitions
# if a column is part of CEA tasks, it has to be of type OBJECT no matter what the type detections says
DEDUCE_FROM_TARGETS = True

# Maximum (batch_size) instances we retrieve labels for...
LABELS_FOR_BATCH_SIZE = 100000

# CEA strategies priorities
if TARGET_KG == WIKIDATA:
    Generic_priority = 0
    FullCell_priority = 1
    Selective_priority = 3
    Autocorrect_priority = 4
    Token_priority = 3
    AllToken_priority = 2
    CLEAN_CELL_SEPARATOR = ' '
elif TARGET_KG == DBPEDIA:
    Generic_priority = 0
    FullCell_priority = 1
    Selective_priority = 2
    Autocorrect_priority = 3
    Token_priority = 4
    AllToken_priority = 4
    CLEAN_CELL_SEPARATOR = '_'

# file to use in testing
TEST_FILE = 'YBK3P707'

# Time in (mins) pipeline should take to finish one table, if exceeded, Timeout exception will be raised
PIPELINE_SLA_SEC = 60 * 60  #10 mins

ENABLE_PARTIAL_RES_SUBMISSION = True

# This boolean decides which method is used to select CTA
# --- True will activate LCS method
# --- False will activate majority vote method
LCS_SELECT_CTA = False