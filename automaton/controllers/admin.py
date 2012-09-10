import datetime
import gevent
import json
import sqlite3
from envy.controller import Controller
from envy.response import Response
from node import Node
from node.sensor.temperature import Temperature
from node.sensor.humidity import Humidity
from node.sensor.ph import PH
from node.output import Output

SENSORS = dict(
    temperature=Temperature,
    ph=PH,
    humidity=Humidity,
)

class Admin(Controller):

    def index(self):
        home = self.request.env.get('HTTP_HOST')        
        
        con = sqlite3.connect("test.db")
        try:
            con.execute('''CREATE TABLE nodes (blob text)''')
        except Exception as e:
            print e
        cur = con.cursor()        

        n = Node(name='Aquaponics:Lettuce', connect=False)
        ph = PH(0, 'PH', 'ph', n)
        temp = Temperature(1, 'Ambient Temperature', 'ambient_temperature', n)
        humidity = Humidity(2, 'Ambient Humidity', 'ambient_humidity', n)
        n.sensors = [ph, temp, humidity]

        fan = Output(0, 'Cooling Fan', 'cooling_fan', n)
        pump = Output(1, 'Aqua Pump', 'aqua_pump', n)
        plant_light = Output(2, 'Plant Light', 'plant_light', n)
        aqua_light = Output(3, 'Aqua Light', 'aqua_light', n)
        drainage_pump = Output(4, 'Drainage Pump', 'drainage_pump', n)
        n.outputs = [fan, pump, plant_light, aqua_light, drainage_pump]

        #cur.execute("INSERT into nodes VALUES (?)", (n,))
        con.commit()
        res = {}
        return Response(self.render("admin.html", values=json.dumps(res), url=home))

    def save(self):
        ws = self.request.env['wsgi.websocket']
        while True:
            mes = ws.receive()
            mes = json.loads(mes)
            objs = dict()
            print mes
            res = dict(name=mes.get('name'), sensors=[], outputs=[], inputs=[], triggers=[])
            for k,v in mes.iteritems():
                try:
                    type, index, key = k.split('_')
                except: continue                
                ob = objs.get('%ss_%s'%(type, index), {})
                ob[key] = v
                objs['%ss_%s'%(type, index)] = ob

            print objs
            for k,v in objs.iteritems():
                name, i = k.split("_")
                res.get(name).append(v)

            print res
            ws.send('');
            gevent.sleep(.1)


