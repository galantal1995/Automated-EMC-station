
#include <SoftwareSerial.h>
#include "MeOrion.h"

MeStepper stepper1(PORT_1);
MeStepper stepper2(PORT_2);

MeLimitSwitch switch_3_1(PORT_3, SLOT1);
MeLimitSwitch switch_3_2(PORT_3, SLOT2);
MeLimitSwitch switch_6_1(PORT_6, SLOT1);
MeLimitSwitch switch_6_2(PORT_6, SLOT2);
MeLimitSwitch switch_7_2(PORT_7, SLOT2);  // Emergency button

// A and B values are coming from python through the serial port. (input_values() void loop at the end of this code.)
float A;
float B;

int waiting_for_values = 0;
int incoming[4];   // The 2 input values (A and B side of the board) are collectd in this array.
String string1;
String string2;
String string3;
String string4;

String A_string;
String B_string;

float one_revolution_mm     = 36.8575;
int   one_revolution_step   = 3205;

void setup(){
  Serial.begin(11520);
  input_values();
  stepper1.setMaxSpeed(10000);
  stepper1.setAcceleration(20000);
  stepper2.setMaxSpeed(10000);
  stepper2.setAcceleration(20000);
  
}
void loop(){
  if(Serial.available()){
    int coordinate = Serial.parseInt();
    if (coordinate == 0){
      stepper1.moveTo(0);
      stepper2.moveTo(0);
    }
    if (coordinate > 0 && coordinate <= A){
      stepper1.moveTo((coordinate/one_revolution_mm)*one_revolution_step);
    }
    if (coordinate < 0 && coordinate >= (-B)){
      stepper2.moveTo((coordinate/one_revolution_mm)*one_revolution_step);
    }

  }
  stepper1.run();
  stepper2.run();
  if (switch_3_1.touched())
  {
    exit(0);
  }
    
  if (switch_3_2.touched())
  {
    exit(0);
  }
    
  if (switch_6_1.touched())
  {
    exit(0);
  }

  if (switch_6_2.touched())
  {
    exit(0);
  }  
  if (switch_7_2.touched())   // If the emergency button is pressed, the same thing happens. The measuring process stops.
  {
    exit(0);
  } 
}

void input_values(){
  while(waiting_for_values==0){
    while(Serial.available()==4){
      for(int i=0; i<11; i++){
        incoming[i] = Serial.read();
      }
      waiting_for_values = 1;
    }
  }
  string1 = String(incoming[0]);
  string2 = String(incoming[1]);
  string3 = String(incoming[2]);
  string4 = String(incoming[3]);

  if(incoming[1]>9){
    string2 = "";
  }
  if(incoming[3]>9){
    string4 = "";
  }

  A_string = string1+string2;
  B_string = string3+string4;

  // Here comes the important calculation part. The following values will be used during the robot movement.
  A = A_string.toFloat();
  B = B_string.toFloat();
}
