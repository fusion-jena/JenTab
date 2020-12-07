from datetime import datetime
import logging as log
import coloredlogs
import sys
import traceback

a = None
b = None


def init(filename=None, level=log.INFO):
    log.basicConfig(filename=filename, level=level)
    coloredlogs.install(fmt='%(asctime)-15s [%(levelname)s] %(message)s')


def start(method):
    global a
    a = datetime.now()
    log.info(('{0} started at {1}'.format(method, a)).encode('utf-8', errors='ignore'))


def stop(method):
    global b
    b = datetime.now()
    log.info(('{0} ended at: {1}'.format(method, b)).encode('utf-8', errors='ignore'))
    log.info(('{0} took: {1}'.format(method, b - a)).encode('utf-8', errors='ignore'))


def info(message):
    log.info(message.encode('utf-8', errors='ignore'))


def error(message):
    log.error(message.encode('utf-8', errors='ignore'))
    traceback.print_exc(file=sys.stdout)
