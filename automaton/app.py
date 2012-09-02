try:        
    from envy.wsgi import WSGI
    from urls import urls
    from envy.session import CookieSession
    import logging
    import settings    
    from loggers import Logger
    from interface import Interface    

    logging.basicConfig(format=settings.LOG_FORMAT, level=settings.LOG_LEVEL)

    server_settings = dict(
        template_dirs=settings.TEMPLATE_DIRS, 
        session_key='session_id', 
        session_cls=CookieSession
    )

    wsgi = WSGI(urls, server_settings)

    i = Interface(uri="tcp://*:5555")
    l = Logger()

except Exception as e:
    logging.exception(e)

def serve(env, start_response):
    try:
        return wsgi.serve(env, start_response)
    except Exception as e:
        logging.exception(e)
