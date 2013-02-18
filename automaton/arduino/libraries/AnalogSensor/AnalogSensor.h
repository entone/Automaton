#ifndef AnalogSensor_h
#define AnalogSensor_h

#define NUM_READS 10

#include "Arduino.h"

class AnalogSensor{
	public:
		AnalogSensor(uint8_t pin, int output);
		int read();
		void write();
	private:
		bool _started;
		int _pin;
		int _output;
		int _avg[NUM_READS];
		int _total;
		int _index;
};

#endif