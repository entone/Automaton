try:
    import logging
    import signal
    from envy.wsgi import WSGI    
    from models.user import Session
    from pymongo.connection import Connection
    import humongolus as orm    
    from models.node import Sensor
    import settings    
    from urls import urls

    logging.basicConfig(format=settings.LOG_FORMAT, level=settings.LOG_LEVEL)

    server_settings = dict(
        template_dirs=settings.TEMPLATE_DIRS, 
        session_key='automaton_session', 
        session_cls=Session
    )

    if settings.IS_CLOUD:
        conn = Connection()
        logger = logging.getLogger("humongolus")
        orm.settings(logger=logger, db_connection=conn)

        for k,v in settings.SENSORS.iteritems():
            s = Sensor()
            s.type=k
            s.decorator = v
            try:
                s.save()
            except Exception as e:
                logging.warning("%s already instantiated" % k)

    wsgi = WSGI(urls, server_settings)

except Exception as e:
    print e
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
