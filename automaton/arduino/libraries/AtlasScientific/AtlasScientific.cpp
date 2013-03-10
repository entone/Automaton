#include "Arduino.h"
#include "AltSoftSerial.h"
#include "AtlasScientific.h"

AtlasScientific::AtlasScientific(bool ph_active, bool ec_active, bool do_active, bool orp_active)
	: AltSoftSerial(){
		_current_channel = 0;
		_data.reserve(30);
		active_channels[0] = ph_active;
		active_channels[1] = ec_active;
		active_channels[2] = do_active;
		active_channels[3] = orp_active;
		float _values[NUM_VALUES] = {0.00};
		running = false;
}

void AtlasScientific::start(){
	pinMode(PIN0, OUTPUT);
 	pinMode(PIN1, OUTPUT);

 	command(PH_CHANNEL, "E");
 	command(EC_CHANNEL, "E");
 	command(DO_CHANNEL, "E");
 	command(ORP_CHANNEL, "E");
}

bool AtlasScientific::data_available(){
	if(!running){
		running = true;
		command(_current_channel, "R");
		return false;
	}
	//Serial.print("Reading: ");
	//Serial.println(_current_channel);
	while(available()){
    	char in = (char)read();    	
    	_data+=in;
    	if(in == '\r'){
    		_parse_serial(_data);
			_data = "";
			return true;
    	}
    	if(in == -1){
    		Serial.println("Bad Data: " + _data);
    		_data = "";
    		break;
    	}
  	}
  	return false;
}

void AtlasScientific::_open_channel(int channel){
	//Serial.print("Open Channel: ");
	//Serial.println(channel);
	switch(channel){
		case PH_CHANNEL:
			digitalWrite(PIN0, LOW);
			digitalWrite(PIN1, LOW);
			break;
		case EC_CHANNEL:
			digitalWrite(PIN0, HIGH);
			digitalWrite(PIN1, LOW);
			break;
		case DO_CHANNEL:
			digitalWrite(PIN0, LOW);
			digitalWrite(PIN1, HIGH);
			break;
		case ORP_CHANNEL:
			digitalWrite(PIN0, HIGH);
			digitalWrite(PIN1, HIGH);
			break;		
	}	
	delay(100);
	print('\r');
	return;
}

void AtlasScientific::_open_next_channel(){
	_current_channel+=1;
	if(_current_channel < 4 && active_channels[_current_channel]){
		command(_current_channel, "R");
	}
	if(_current_channel < 4 && !active_channels[_current_channel]){
		_open_next_channel();
	}
	if(_current_channel >= 4){
		_current_channel = 0;
		command(_current_channel, "R");
	}
	return;
}

void AtlasScientific::command(int channel, String command){
	_open_channel(channel);
	print(command+"\r");
}

void AtlasScientific::_parse_serial(String command){
  	int numArgs = 0;
  	int beginIdx = 0;
  	int idx = command.indexOf(",");

  	String arg;
  	char charBuffer[32];

	while (idx != -1){
		arg = command.substring(beginIdx, idx);
		arg.toCharArray(charBuffer, 32);

		// add error handling for atoi:
		_values[numArgs++] = atof(charBuffer);
		beginIdx = idx + 1;
		idx = command.indexOf(",", beginIdx);
	}
	arg = command.substring(beginIdx);
	arg.toCharArray(charBuffer, 32);
	_values[numArgs++] = atof(charBuffer);
}

void AtlasScientific::_print(int output, int index){
	Serial.print(output);
	Serial.print(",");
	Serial.println(_values[index]);
}

void AtlasScientific::write(){
	switch(_current_channel){
		case PH_CHANNEL:
			_print(PH_OUTPUT, 0);
			break;
		case EC_CHANNEL:
			_print(EC_OUTPUT, 0);
			_print(TDS_OUTPUT, 1);
			_print(SALINITY_OUTPUT, 2);
			break;
		case DO_CHANNEL:
			_print(DO_PERCENTAGE_OUTPUT, 0);
			_print(DO_OUTPUT, 1);
			break;
		case ORP_CHANNEL:
			_print(ORP_OUTPUT, 0);
			break;
	}
	_open_next_channel();
}