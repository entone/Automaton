import math
import gevent
from pid import PID

JOULES_GRAM = 4.186 #joules to heat 1gram of water 1degree celcius
PI = 3.14
POLYETHALENE_K = .5#K value of Polyethalene
JOULES_CALORIE = 4187#joules in a calorie
JOULES_CELCIUS = 0.000526565076466

class WaterTank(object):
    liters = 100
    desired_temp = 27
    input_wattage = 500 
    outside_temp = 20

    def __init__(self, desired_temp, outside_temp, input_wattage, r, h, thickness):
        self.r = r
        self.h = h
        self.d = 2*r
        self.thickness = thickness
        self.volume = volume = (PI*h*math.pow(r, 2))/1000#liters
        self.current_temp = desired_temp

        sides = (2*PI)*r*h
        base = PI*math.pow(r, 2)
        self.surface_area = (sides+base)/10000
        print "Surface Area: %sm" % self.surface_area
        print "Liters: %s" % self.volume

        self.weight = volume#kg
        self.total_joules = self.weight*JOULES_CALORIE

        print "Total Joules: %s" % self.total_joules

        self.desired_temp = desired_temp
        self.outside_temp = outside_temp
        self.input_wattage = input_wattage

        self.pid = PID(3.0,0.4,1.2)
        self.pid.setPoint(self.desired_temp)

        self.run()
        

    def heat(self, time):
        global JOULES_CELCIUS
        print "Heating!"
        total_watts = self.input_wattage*time
        self.current_temp+= (total_watts*JOULES_CELCIUS)/(self.volume*1000)
        print self.current_temp

    def run(self):
        global POLYETHALENE_K, JOULES_CELCIUS
        while True:
            pid = self.pid.update(self.current_temp)
            print pid
            if pid > 1: 
                self.heat(pid)
                gevent.sleep(1)
                continue
            heat_loss = (POLYETHALENE_K*self.surface_area*(self.desired_temp-self.outside_temp)/self.thickness)/3600
            celc_change = (heat_loss*JOULES_CELCIUS)
            print "Heat Loss: %s" % celc_change
            self.current_temp-= celc_change
            print "Temp: %s" % self.current_temp
            gevent.sleep(1)
            
            


wt = WaterTank(desired_temp=27, outside_temp=20, input_wattage=2600, r=50, h=50, thickness=.005)









