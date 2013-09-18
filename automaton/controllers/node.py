from flask import current_app, request, Blueprint, render_template, Response
import gevent
from automaton import settings
import random
import json

node = Blueprint(
    'node',
    __name__,
    template_folder='../html/templates/'
)

@node.route('/', methods=['GET'])
def display():
    return render_template("stream.html");

@node.route('/stream/')
def stream():
    try:
        ws = request.environ['wsgi.websocket']
        current_app.logger.info(ws)
    except Exception as e:
        current_app.logger.exception(e)    
    while True:
        try:
            ws.send(json.dumps({"int":random.randint(1, 10000)}))
        except Exception as e:
            return Response()
        gevent.sleep(1)

