try:
    from envy.wsgi import WSGI
    from urls import urls
    from envy.session import CookieSession
    import logging
    import settings    
    import signal
    from loggers import Logger

    logging.basicConfig(format=settings.LOG_FORMAT, level=settings.LOG_LEVEL)

    server_settings = dict(
        template_dirs=settings.TEMPLATE_DIRS, 
        session_key='session_id', 
        session_cls=CookieSession
    )
    print server_settings

    wsgi = WSGI(urls, server_settings)

except Exception as e:
    logging.exception(e)

def log_request(self):
    log = self.server.log
    if log:
        if hasattr(log, "info"):
            log.info(self.format_request())
        else:
            log.write(self.format_request())

import gevent
gevent.pywsgi.WSGIHandler.log_request = log_request
gevent.signal(signal.SIGQUIT, gevent.shutdown)

def serve(env, start_response):
    try:
        logging.info(server_settings)
        return wsgi.serve(env, start_response)
    except Exception as e:
        logging.exception(e)
