#include <AnalogSensor.h>
#include <AtlasScientific.h>
#include <SoftwareSerial.h>

#define EC 0
#define TDS 1
#define SALINITY 2
#define PH 6

#define LIGHTS 13

//AtlasScientific ec = AtlasScientific(8,9);
AtlasScientific ph = AtlasScientific(8,9);

AnalogSensor temp = AnalogSensor(A0, 3);
AnalogSensor humidity = AnalogSensor(A1, 4);
AnalogSensor water_temp = AnalogSensor(A2, 5);
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
    ph.begin(38400);
    //ec.begin(38400);
    delay(1000);
    ph.command("C");
    //ec.command("C");
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
  /*
  if(ec.data_available()){
    ec.write(EC, 0);
    ec.write(TDS, 1);
    ec.write(SALINITY, 2);
  }
  */
  if(ph.data_available()){
    ph.write(PH, 0);
  }
  temp.write();
  humidity.write();
  water_temp.write();
  water_level.write();
  Serial.print("!");
  delay(100);
}
