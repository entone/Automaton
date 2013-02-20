#include <AnalogSensor.h>
#include <AtlasScientific.h>
#include <AltSoftSerial.h>

#define EC 0
#define TDS 1
#define SALINITY 2
#define LIGHTS 13

int ec_value;
int tds_value;
int salinity_value;
int ec_values[3];
bool ec_avail = false;

AtlasScientific ec = AtlasScientific();

AnalogSensor temp = AnalogSensor(A0, 3);
AnalogSensor humidity = AnalogSensor(A1, 4);
AnalogSensor water_temp = AnalogSensor(A2, 5);
AnalogSensor ph = AnalogSensor(A3, 6);
AnalogSensor water_level = AnalogSensor(A4, 7);

String input;

void parse_serial(String command, int *args){
  int numArgs = 0;
  int beginIdx = 0;
  int idx = command.indexOf(",");

  String arg;
  char charBuffer[16];

  while (idx != -1){
      arg = command.substring(beginIdx, idx);
      arg.toCharArray(charBuffer, 16);
  
      // add error handling for atoi:
        args[numArgs++] = atoi(charBuffer);
      beginIdx = idx + 1;
      idx = command.indexOf(",", beginIdx);
  }
  arg = command.substring(beginIdx);
  arg.toCharArray(charBuffer, 16);
  args[numArgs++] = atoi(charBuffer);
}

void setup(){
    input.reserve(20);
    Serial.begin(9600);
    ec.begin(38400);
    delay(1000);
    ec.command("C");
    pinMode(LIGHTS, OUTPUT);
}

void serialEvent() {
    while (Serial.available()) {
        // get the new byte:
        char inChar = (char)Serial.read(); 
        // add it to the inputString:
        input+=inChar;
        // if the incoming character is a newline, set a flag
        // so the main loop can do something about it:
        if (inChar == '\r') {
            int data[2];
            parse_serial(input, data);
            digitalWrite(data[0], data[1]);
            input = "";
        } 
    }
}

void loop(){
  Serial.print("@");
  if(ec.data_available()){
    ec.write(EC, ec_values[0]);
    ec.write(TDS, ec_values[1]);
    ec.write(SALINITY, ec_values[2]);
  }
  temp.write();
  humidity.write();
  water_temp.write();
  ph.write();
  water_level.write();
  Serial.print("!");
  delay(100);
}