from flask import Flask
from automaton.controllers.realtime import node
from automaton import settings
import logging
import gevent.pywsgi
from flask.ext.mako import MakoTemplates

logging.basicConfig(format=settings.LOG_FORMAT, level=settings.LOG_LEVEL)

def log_request(self):
    log = self.server.log
    if log:
        if hasattr(log, "info"):
            log.info(self.format_request() + '\n')
        else:
            log.write(self.format_request() + '\n')

gevent.pywsgi.WSGIHandler.log_request = log_request

class Automaton(Flask): pass

def create_app():
    app = Automaton(__name__)    
    app.config.from_object('automaton.settings')
    app.register_blueprint(node)
    mako = MakoTemplates(app)
    handler = logging.handlers.SysLogHandler(facility=logging.handlers.SysLogHandler.LOG_SYSLOG)
    app.logger.addHandler(handler)
    return app