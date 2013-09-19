import gevent
import sqlite3
import datetime
import simplejson as json
import base64
import logging
from gevent import socket
from gevent.select import select
from automaton import settings
from automaton.util.broadcast.udpserver import UDPServer
from automaton.util import aes
from automaton.util.jsontools import ComplexEncoder
#from automaton.util.cloud import Cloud
#from automaton.util.download_image import DownloadImage
#from automaton.loggers import Logger, CloudLogger


class Manager(UDPServer):
    nodes = dict()

    def __init__(self):
        super(Manager, self).__init__()
        self.nodes = dict()
        #self.clients_pubsub = UDPServer()
        #self.nodes_pubsub = PubSub(self, pub_port=settings.NODE_SUB, sub_port=settings.NODE_PUB, parse_message=self.parse_message)
        self.logger = logging.getLogger(__name__)
        #self.cloud = Cloud()
        #self.register()        
        #Logger(self)
        #CloudLogger(self)
        while True: gevent.sleep(0)

    def register(self):
        self.db = sqlite3.connect("automaton.db", detect_types=sqlite3.PARSE_DECLTYPES)
        c = self.db.cursor()
        try:
            c.execute('''CREATE TABLE registration (id text)''')
        except Exception as e: pass
        self.logger.info("Table Created")
        c.execute("SELECT id FROM registration")
        self.id = c.fetchone()
        self.logger.info(self.id)     
        if not self.id:
            res = self.cloud.register_location()
            c.execute("INSERT INTO registration VALUES (?)", (res.get('id'),))
            self.id = res.get('id')
            self.db.commit()
            self.logger.info(self.id)
        else:
            self.id = self.id[0]

        c.close()

    def encrypt(self, message):
        return aes.encrypt(json.dumps(message, cls=ComplexEncoder), settings.KEY)

    def decrypt(self, message):
        for k,n in self.nodes.iteritems():
            try:
                return n.parse_message(message)
            except Exception as e:
                self.logger.exception(e)
        
        try:
            return aes.decrypt(message, settings.KEY)
        except Exception as e:
            self.logger.exception(e)
            return message

    def add_node(self, obj, address, **kwargs):
        rpc_port = settings.NODE_RPC+len(self.nodes.keys())
        key = aes.generate_key()
        n = Node(name=obj.get('name'), address=address, port=rpc_port, key=key)
        self.nodes[n.name] = n
        n.publish(method='initialize_rpc', message=dict(port=rpc_port, key=base64.urlsafe_b64encode(key)), key=settings.KEY)        
        return True

    def get_node(self, name):
        return self.nodes.get(name)

    def initialized(self, obj, address, **kwargs):
        node = self.get_node(obj.get('name'))
        if node: 
            obj = node.call(method='hello')
            self.logger.info("Yeah!")
            self.logger.info(obj)
            node.set_obj(obj)  
            #if not obj.get('id'):
                #obj['location_id'] = self.id
                #res = self.cloud.add_node(obj)
                #self.logger.info(res)
                #mes = dict(id=res.get('id'))
                #node.id = res.get('id')
                #success = node.call(method='set_id', message=mes)

            #node.downloader = DownloadImage(node.id, "%s%s" % (node.webcam, settings.TIMELAPSE_PATH), settings.TIMELAPSE_SAVE_PATH, settings.TIMELAPSE_PERIOD, s3=True, cb=self.log_image)

        return True

    def log_image(self, filename, id):
        ts = datetime.datetime.utcnow()
        #self.cloud.save_image(dict(timestamp=ts, location=self.id, node=id, filename=filename))

    def get_nodes(self, obj):
        return [n.call('json') for k,n in self.nodes.iteritems()]

    def get_sensor_values(self):
        res = dict(location_id=self.id, nodes=[])
        for k, n in self.nodes.iteritems():
            res['nodes'].append(n.call('get_sensor_values'))

        return res

    def node_change(self, obj, address):
        #obj['location_id'] = self.id
        mes = json.dumps(obj, cls=ComplexEncoder)
        mes = aes.encrypt(mes, settings.KEY)
        #self.clients_pubsub.publish(mes)
        return True

    def set_output_state(self, obj):
        node = self.get_node(obj.get('node'))
        res = node.call('set_output_state', obj)

    def parse_message(self, message):
        for k,n in self.nodes.iteritems():
            try:
                return n.parse_message(message)
            except Exception as e:
                self.logger.exception(e)

        try:
            return aes.decrypt(message, settings.KEY)
        except Exception as e:
            self.logger.exception(e)
            return message



class Node(object):

    def __init__(self, name, address, port, key):
        self.name = name
        self.port = port
        self.address = address
        self.pubsub = UDPServer(spawn=False)
        self.key = key
        self.id = None
        self.logger = logging.getLogger(__name__)

    def set_obj(self, obj):
        self.obj = obj
        for k,v in obj.iteritems(): setattr(self, k, v)

    def publish(self, method, message=None, key=None):
        key = key if key else self.key
        message = message if message else {}
        message['method'] = method
        self.logger.debug("Publishing: %s" % message)
        message = json.dumps(message, cls=ComplexEncoder)
        message = aes.encrypt(message, key)
        st = self.name+message
        self.pubsub.broadcast(st)
        return True

    def call(self, method, message=None):
        message = message if message else {}
        message['name'] = self.name
        message['method']=  method
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
        msg = aes.encrypt(json.dumps(message), self.key)
        add = (self.address[0], self.port)
        sock.sendto(msg, add)
        while True:
            result = select([sock],[],[])
            for s in result[0]:
                msg, address = s.recvfrom(1048576)
                msg = self.parse_message(msg)
                msg = json.loads(msg)
                sock.close()
                return msg

            gevent.sleep(0)

    def parse_message(self, message):
        return aes.decrypt(message, self.key)
