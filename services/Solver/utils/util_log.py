from datetime import datetime
import logging as log

a = None
b = None

# initialize
logger = log.getLogger( 'JenTab' )
format = log.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
handler = log.StreamHandler()
handler.setFormatter(format)
logger.addHandler(handler)
logger.propagate = False

def init(filename, level=log.INFO):
    # log.basicConfig(filename=filename, level=level)
    pass


def start(method):
    global a
    a = datetime.now()
    log.info(('{0} started at {1}'.format(method, a)).encode('utf-8', errors='ignore'))


def stop(method):
    global b
    b = datetime.now()
    logger.info(('{0} ended at: {1}'.format(method, b)).encode('utf-8', errors='ignore'))
    logger.info(('{0} took: {1}'.format(method, b - a)).encode('utf-8', errors='ignore'))


def info(message):
    logger.info(message.encode('utf-8', errors='ignore'))


def debug(message):
    logger.debug(message.encode('utf-8', errors='ignore'))


def error(message):
    logger.error(message)
