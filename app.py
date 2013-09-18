import os
import sys
from automaton import create_app

def run(env, start_response):    
    _application = create_app()    
    app = _application(env, start_response)    
    return app
