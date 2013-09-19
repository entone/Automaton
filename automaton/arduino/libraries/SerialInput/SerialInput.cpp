#include "Arduino.h"
#include "SerialInput.h"

SerialInput::SerialInput(){
	_input.reserve(200);
}

void SerialInput::begin(HardwareSerial *ser, int baud){
	_serial = ser;
	_serial->begin(baud);
	_serial->println("Rockin");
}

void SerialInput::loop(int *args){
	while (_serial->available()) {
    	// get the new byte:
    	char inChar = (char)_serial->read(); 
	    // add it to the inputString:
	    _input+=inChar;
	    // if the incoming character is a newline, set a flag
	    // so the main loop can do something about it:
	    if (inChar == '\r') {
	      	int numArgs = 0;
			int beginIdx = 0;
			int idx = _input.indexOf(",");

			String arg;
			char charBuffer[16];

			while (idx != -1){
				arg = _input.substring(beginIdx, idx);
				arg.toCharArray(charBuffer, 16);

				// add error handling for atoi:
				args[numArgs++] = atoi(charBuffer);
				beginIdx = idx + 1;
				idx = _input.indexOf(",", beginIdx);
			}
			arg = _input.substring(beginIdx);
			arg.toCharArray(charBuffer, 16);
			args[numArgs++] = atoi(charBuffer);
	      	_input = "";
	    } 
  	}
}