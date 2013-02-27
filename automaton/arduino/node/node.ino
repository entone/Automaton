#include <AnalogSensor.h>
#include <AtlasScientific.h>
#include <AltSoftSerial.h>

#define LIGHTS 13
#define PH_ACTIVE true
#define EC_ACTIVE false
#define DO_ACTIVE true
#define ORP_ACTIVE false

AtlasScientific as = AtlasScientific(PH_ACTIVE, EC_ACTIVE, DO_ACTIVE, ORP_ACTIVE);

AnalogSensor temp = AnalogSensor(A0, 7);
AnalogSensor humidity = AnalogSensor(A1, 8);
AnalogSensor water_temp = AnalogSensor(A2, 9);
AnalogSensor water_level = AnalogSensor(A4, 10);

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
    as.begin(38400);
    as.start();
    delay(1000);
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
  if(as.data_available()){
    as.write();
  }
  temp.write();
  humidity.write();
  water_temp.write();
  water_level.write();
  Serial.print("!");
  delay(100);
}
