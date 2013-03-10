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

bool paused;

void parse_serial(String command, String *args){
    int numArgs = 0;
    int beginIdx = 0;
    int idx = command.indexOf("|");

    String arg;

    while (idx != -1){
        arg = command.substring(beginIdx, idx);
        args[numArgs++] = arg;
        beginIdx = idx + 1;
        idx = command.indexOf("|", beginIdx);
    }
    arg = command.substring(beginIdx);
    args[numArgs++] = arg;
}

void setup(){
    paused = false;
    input.reserve(20);
    Serial.begin(9600);
    as.begin(38400);
    delay(1000);
    as.start();
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
        if (inChar == '\r'){
            String data[3];
            parse_serial(input, data);
            if(data[0] == "S"){
                char pin[16];
                data[1].toCharArray(pin, 16);
                as.command(atoi(pin), data[2]);
            }
            if(data[0] == "D"){
                char pin[16];
                data[1].toCharArray(pin, 16);
                char val[16];
                data[2].toCharArray(val, 16);
                digitalWrite(atoi(pin), atoi(val));
            }
            if(data[0] == "P"){
                paused = true;
            }
            if(data[0] == "R"){
                paused = false;
            }
            input = "";
        } 
    }
}

void loop(){
    if(!paused){
        if(as.data_available()){
            as.write();
        }
        temp.write();
        humidity.write();
        water_temp.write();
        water_level.write();
    }
    delay(100);
}
