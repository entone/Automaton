# -*- coding: utf-8 -*-

from node.sensor import Sensor

class Temperature(Sensor):
    type="temperature"
    decorator="˚C"

    def conversion(self, value):
        mV = value * 4.9
        return (mV-500)/10