#ifndef AtlasScientific_h
#define AtlasScientific_h
#define BAUD 38400
#define NUM_VALUES 3

#include "Arduino.h"
#include "AltSoftSerial.h"

class AtlasScientific: public AltSoftSerial{
	public:
		AtlasScientific();
		void command(String command);
		void write(int output, int value_index);
		void loop();
		bool data_available;
	private:
		String _data;
		void _parse_serial(String command);
		int _output;
		int _values[NUM_VALUES];
};

#endif