import os

# enable/disable model based corrections
ENABLE_MODELBASED_CORRECTIONS = True and not os.environ.get('DISABLE_MODELBASED_CORRECTIONS', False)

# enable/disable model based corrections using Wikipedia VOCAB
ENABLE_WIKIPEDIA_CORRECTION = False

# enable/disable off_the_shelf corrections
ENABLE_OFF_THE_SHELF_CORRECTIONS = False

# enable/disable Wikidata nearest label corrections
ENABLE_WIKIDATA_BASED_CORRECTIONS = False

# degree of parallelization for autocorrection
AUTOCORRECT_PARALLEL = 4

# maximum number of autocorrected entries
AUTOCORRECT_MAX = 1000

# Model based corrections uses this value to split the clean cell
# if you are using DBpedia, set to '_'
# if you are using Wikidata, set to ' '
CLEAN_CELL_SEPARATOR = ' '

# Loading big files chunks
chunk_size = 200 * 1024 * 1024 # 200 MB file size

# init number of used CPUs
import multiprocessing
# cpus = 1
try:
    cpus = multiprocessing.cpu_count()
except NotImplementedError:
    cpus = 2  # arbitrary default

import os
# internal_storage_config
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
if os.environ.get('DOCKERIZED', False):
    CACHE_PATH = os.path.join(CUR_PATH, 'cache')
    ASSET_PATH = os.path.join(CUR_PATH, 'assets')
else:
    CACHE_PATH = os.path.abspath(os.path.join(CUR_PATH, '..', '..', 'assets', 'data', 'cache', 'Autocorrect'))
    ASSET_PATH = os.path.abspath(os.path.join(CUR_PATH, '..', '..', 'assets', 'Autocorrect'))

# make sure all paths exist
if not os.path.exists(CACHE_PATH):
    os.makedirs(CACHE_PATH)
