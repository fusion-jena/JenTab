import os
# sample: https://github.com/benoitc/gunicorn/blob/master/examples/example_config.py

# listing address
bind = '0.0.0.0:5006'

# number of workers
workers = os.environ.get('SERVICE_WORKERS', 5)

# logging to stdout
errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# increase worker timeout
timeout = 600
