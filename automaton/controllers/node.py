from flask import current_app, request, Blueprint
from automaton import settings
import sqlite3

node = Blueprint(
    'node',
    __name__,
    template_folder='../html/templates/'
)

@node.route('/', methods=['GET'])
def display():
    res = {}
    self.rpc = RPC(port=settings.CLIENT_RPC, address='127.0.0.1')
    res = self.rpc.send(dict(method='get_nodes'), settings.KEY)
    db = sqlite3.connect("automaton.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cur = db.cursor()
    q_t = datetime.datetime.utcnow()-datetime.timedelta(hours=settings.HISTORICAL_DISPLAY)
    for n in res:
        n['historical'] = cur.execute('SELECT * FROM logs WHERE node=? AND timestamp > ? LIMIT 20', (n.get('name'),q_t)).fetchall()
    
    current_app.logger.debug("Got Nodes: %s" % res)
    db.close()
    return render_template("base.html", values=json.dumps(res, cls=ComplexEncoder))

@node.route('/historical/<name>', methods=['GET'])
def historical(name):
    db = sqlite3.connect("automaton.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cur = db.cursor()
    q_t = datetime.datetime.utcnow()-datetime.timedelta(hours=settings.HISTORICAL_DISPLAY)
    res = cur.execute('SELECT * FROM logs WHERE node=? AND timestamp > ?', (name,q_t)).fetchall()
    self.logger.debug(res)
    return Response(json.dumps(res, cls=ComplexEncoder))

@node.route('/index', methods=['GET'])
def index():
    ws = request.environ['wsgi.websocket']
    def write_out(ob):
        try:
            st = "%s\n" % json.dumps(ob, cls=ComplexEncoder)
            self.logger.debug("Message: %s" % st)
            ws.send(st)
            return True
        except Exception as e:
            self.logger.info("Connection Closed: %s" % ws)
            return False
    sub = Subscriber(callback=write_out, port=settings.CLIENT_SUB, broadcast=False, spawn=False, parse_message=parse_message)
    return Response('')
    
def parse_message(message):
    return aes.decrypt(message, settings.KEY)

@node.route('/control', methods=['GET'])
def control():
    rpc = RPC(port=settings.CLIENT_RPC)
    mes = request.json()
    mes['method'] = 'set_output_state'
    res = rpc.send(mes, settings.KEY)
    return Response(json.dumps(res, cls=ComplexEncoder))

