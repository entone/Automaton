#include "Arduino.h"
#include "AnalogSensor.h"

AnalogSensor::AnalogSensor(uint8_t pin, int output){
	_pin = pin;
	_output = output;
	_index = 0;
	_total = 0;
	_started = false;
}

int AnalogSensor::read(){
	if(_index >= NUM_READS){
		if(!_started){
			_started = true;
		}
		_index = 0;
	}
	int val = analogRead(_pin);
	_total = _total-_avg[_index];
  	_avg[_index] = val;
  	_total = _total+val;
  	_index = _index+1;
  	if(!_started) return val;
  	return _total/NUM_READS;
}

void AnalogSensor::write(){
	Serial.print(_output);
	Serial.print(",");
	Serial.println(read());
}