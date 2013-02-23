#ifndef AtlasScientific_h
#define AtlasScientific_h
#define BAUD 38400
#define NUM_VALUES 3

#include "Arduino.h"
#include "SoftwareSerial.h"

class AtlasScientific: public SoftwareSerial{
	public:
		AtlasScientific(uint8_t rx, uint8_t tx);
		void command(String command);
		void write(int output, int value_index);		
		bool data_available();
	private:
		String _data;
		void _parse_serial(String command);
		int _values[NUM_VALUES];
};

#endif