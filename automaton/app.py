try:    
    from envy.wsgi import WSGI    
    from urls import urls
    from envy.session import CookieSession
    import logging
    import settings
    import models
    import controllers
    import gevent
    import loggers
    from interface import Interface    

    logging.basicConfig(format=settings.LOG_FORMAT, level=settings.LOG_LEVEL)

    server_settings = dict(
        template_dirs=settings.TEMPLATE_DIRS, 
        session_key='session_id', 
        session_cls=CookieSession
    )

    wsgi = WSGI(urls, server_settings)

    loggers.init()

    i = Interface()
    i.humidity_event+=loggers.humidity
    i.ph_event+=loggers.ph
    gevent.spawn(i.run)
except Exception as e:
    logging.exception(e)

def serve(env, start_response):
    try:
        return wsgi.serve(env, start_response)
    except Exception as e:
        logging.exception(e)
