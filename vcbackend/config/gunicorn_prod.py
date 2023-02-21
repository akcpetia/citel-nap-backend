"""Gunicorn *development* config file"""

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "vcbackend.wsgi:application"
# The granularity of Error log outputs
loglevel = "debug"
# The number of worker processes for handling requests
workers = 2
# The socket to bind
bind = "0.0.0.0:8080"
# Restart workers when code changes (development only!)
reload = True
# Write access and error info to /var/log
accesslog = "citel_nap.access.log"
errorlog = "citel_nap.error.log"
# Redirect stdout/stderr to log file
capture_output = True
