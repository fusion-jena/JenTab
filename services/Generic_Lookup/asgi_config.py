import os
# sample: https://github.com/benoitc/gunicorn/blob/master/examples/example_config.py

# listing address
bind = '0.0.0.0:5010'

# workers
workers = os.environ.get('SERVICE_WORKERS', 1)

# logging to stdout
errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# init our database, before starting the server
preload = True
