#ifndef AtlasScientific_h
#define AtlasScientific_h
#define BAUD 38400
#define NUM_VALUES 3

#define PH_CHANNEL 0
#define EC_CHANNEL 1
#define DO_CHANNEL 2
#define ORP_CHANNEL 3

#define PIN0 4
#define PIN1 5

#define PH_OUTPUT 0
#define EC_OUTPUT 1
#define TDS_OUTPUT 2
#define SALINITY_OUTPUT 3
#define DO_PERCENTAGE_OUTPUT 4
#define DO_OUTPUT 5
#define ORP_OUTPUT 6

#include "Arduino.h"
#include "AltSoftSerial.h"

class AtlasScientific: public AltSoftSerial{
	public:
		AtlasScientific(bool ph_active, bool ec_active, bool do_active, bool orp_active);
		void command(int channel, String command);
		bool data_available();
		void write();
		void start();
	private:
		bool running;
		String _data;
		int _current_channel;
		bool active_channels[4];
		void _print(int output, int index);
		void _parse_serial(String command);
		void _open_channel(int channel);
		void _open_next_channel();
		int _values[NUM_VALUES];
};

#endif