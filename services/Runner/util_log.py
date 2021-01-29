from datetime import datetime
import logging as log
import coloredlogs

a = None
b = None


def init(filename=None, level=log.INFO):
    log.basicConfig(filename=filename, level=level)
    coloredlogs.install(fmt='%(asctime)-15s [%(levelname)s] %(message)s')


def start(method):
    global a
    a = datetime.now()
    log.info('{0} started at {1}'.format(method, a))


def stop(method):
    global b
    b = datetime.now()
    log.info('{0} ended at: {1}'.format(method, b))
    log.info('{0} took: {1}'.format(method, b - a))


def info(message):
    log.info(message)


def error(message):
    log.error(message)


def warn(message):
    log.warning(message)
