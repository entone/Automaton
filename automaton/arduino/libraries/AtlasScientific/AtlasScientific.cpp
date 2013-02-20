#include "Arduino.h"
#include "AltSoftSerial.h"
#include "AtlasScientific.h"

AtlasScientific::AtlasScientific()
	: AltSoftSerial(){		
		_data.reserve(30);
		int _values[NUM_VALUES] = {0};
}

void AtlasScientific::loop(){
	while(available()){
    	char in = (char)read();
    	_data+=in;
    	if(in == '\r'){
      		_parse_serial(_data);
      		_data = "";
    	}
  	}
}

void AtlasScientific::command(String command){
	print(command+"\r");
}

void AtlasScientific::_parse_serial(String command){
  	int numArgs = 0;
  	int beginIdx = 0;
  	int idx = command.indexOf(",");

  	String arg;
  	char charBuffer[16];

	while (idx != -1){
		arg = command.substring(beginIdx, idx);
		arg.toCharArray(charBuffer, 16);

		// add error handling for atoi:
		_values[numArgs++] = atoi(charBuffer);
		beginIdx = idx + 1;
		idx = command.indexOf(",", beginIdx);
	}
	arg = command.substring(beginIdx);
	arg.toCharArray(charBuffer, 16);
	_values[numArgs++] = atoi(charBuffer);
}

int AtlasScientific::value(int value_index){
	return _values[value_index];
}

void AtlasScientific::write(int output, int value_index){
	Serial.print(output);
	Serial.print(",");
	int val = _values[value_index];
	Serial.println(val);
}