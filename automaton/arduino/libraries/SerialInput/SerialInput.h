#ifndef SerialInput_h
#define SerialInput_h

#include "Arduino.h"
#include "HardwareSerial.h"


class SerialInput{
	public:
		SerialInput();
		void begin(HardwareSerial *ser, int baud);
		void loop(int *args);
	private:
		String _input;
		HardwareSerial *_serial;
};

#endif