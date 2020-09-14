#include <Wire.h>
#include <SoftwareSerial.h>

#include <MeOrion.h>

double angle_rad = PI/180.0;
double angle_deg = 180.0/PI;

MeStepper stepper_1(PORT_1);  // Responsible for the movement that is parellel to the side of the frame where the controller is placed.
MeStepper stepper_2(PORT_2);  // Responsible for the movement that is vertical to the side of the frame where the controller is placed.

MeLimitSwitch switch_3_1(PORT_3, SLOT1);  
MeLimitSwitch switch_3_2(PORT_3, SLOT2);
MeLimitSwitch switch_6_1(PORT_6, SLOT1);
MeLimitSwitch switch_6_2(PORT_6, SLOT2);
MeLimitSwitch switch_7_2(PORT_7, SLOT2);  // Emergency button


//-------------------------------------------------------------
// These values are coming from python through the serial port. (input_values() void loop at the end of this code.)
float A;             // A [mm] is the side of the PCB which is parellel to the axis where the controller is placed "x-axis".

float B;             // B [mm] is the side of the PCB which is parellel to the axis where the movable motor is placed "y-axis".

float step_mm;       // The distance what the robot moves between two measurements [mm].

float time_delay_after_measurements; // The time delay in millisecond between two measurements.

int measurements_in_one_point; // Number of measurements in one measurement point.

//------------------------------------------------------------
// The input values are coming from python through the Serial port.
// I am using the following variables to read these values and to transform them back to their original shape because on the serial communication only values between 0-255 can be sent. ==> therefore there are some modifications.
int waiting_for_values = 0;
int incoming[11]; // The 6 input value are collectd in this array.
String string1;
String string2;
String string3;
String string4;
String string5;
String string6;
String string7;
String string8;
String string9;
String string10;

String A_string;
String B_string;
String step_mm_string;
String time_delay_after_measurements_string;
String measurements_in_one_point_string;
//---------------------------------------------------

float one_revolution_mm     = 36.8575;     // one revolution of the stepper motor is 36.8575mm
int   one_revolution_step   = 3205;       // this 3205 is the value that has to be given in for the motor to do one revolution.
float step_motor;   // This is the value which has to be given to the motors to run.(stepper.move() ==> command)
float time_of_a_step;
int number_of_steps_xaxis;   // x-axis is the axis which is parellel to the side of cage where the controller is placed.
int number_of_steps_yaxis;
int speed_of_the_motors     = 6000;
int   x = 0;    // it controls the while loop for the steps on the x-axis.
int   y = 0;    // it controls the number of repetitions.
int turn = 1;

// The next six variables are called to control the safety run of the robot befor the measurement.

int safety_round;
int speed_of_the_motors_safety_run    = 2000;  // The safety run is slower than the speed of the real measurement.
float time_of_step_safety_run;
int diameter_of_probe                 = 6;    // If you work with a different probe, this value has to be changed. Measure the outer diameter of the probe and write this value in mm here.
float time_of_step_y_safety_run;
float step_motor_safety_run;
int number_of_steps_yaxis_safety_run;
float remainder;


void setup(){

  Serial.begin(9600);
  input_values();  // Arduino waits until it gets the input values from python and then starts the safety run. You can see how the processing of these values is done in the void input_values() loop.
  
  if (safety_round == 2){   // Do the safety run only if the user selected it in the python gui interface
    safety_run();
  }
  
  
  int   x = 0;    
  int   y = 0;    // To set these variable for the real measurement as they were originally.
  int turn = 1;
  
  _delay(2000);   // Wait 2 seconds between the safety run and the measurement. 
    
  take_a_measurement();
  while(y < (number_of_steps_yaxis))
  {
    while (x < number_of_steps_xaxis)
    {
      stepper_1_movement(step_motor * turn);
      x += 1;
      _delay(time_of_a_step);
      take_a_measurement();
    }
    turn = turn*(-1);
    stepper_2_movement(step_motor * -1);
    x = 0;
    _delay(time_of_a_step);
    take_a_measurement();
    y += 1;
  }
    
  // The last step before the robot goes back to zero. It depends on the size of the PCB.
  // It can be either a left or a right turn depending on the final position of the robot(depends on the size of the PCB where to robot finishes).
  if (number_of_steps_yaxis % 2 == 0){     // if it is even ==> the robot moves on the right.
    while (x < number_of_steps_xaxis)
    {
      stepper_1_movement(step_motor);
      x += 1;
      _delay(time_of_a_step);
      take_a_measurement(); 
    }
  }
  else {        // Else it is odd ==> the robot moves on the left.
    while (x < number_of_steps_xaxis)
    {
      stepper_1_movement(step_motor * -1);
      x += 1;
      _delay(time_of_a_step);
      take_a_measurement();
    }
  }
  _delay(time_of_a_step + 1000);                     // 1000 is there so that after the neccessary part of the plotting is done, the robot waits and then goes back to zero.

  // Go back to the origin
  // Again it depends on the size of the PCB where the robot finishes the measurement. 
  if (number_of_steps_yaxis % 2 == 0) // If ist even ==> Robot goes right and all the was down to where it started.
  {
    stepper_2_movement(number_of_steps_yaxis * step_motor);
    _delay(time_of_a_step * number_of_steps_yaxis + 1000);

    stepper_1_movement(-number_of_steps_xaxis * step_motor);
    _delay(time_of_a_step * number_of_steps_xaxis + 2000);   // This delay is just to wait with breaking the code until the probe is back to the origin.
  }
  else{       // If its odd ==> The robot has to move only down till the origin.
    stepper_2_movement(number_of_steps_yaxis * step_motor);
    _delay((time_of_a_step * number_of_steps_yaxis) + time_of_a_step + 2000);   
  }
  Serial.print(3);  // When the measurement is done, Arduino sends a signal to python (this signal is the 3.)
  exit(0);
}

void loop(){
  stepper_1.runSpeedToPosition();
  stepper_2.runSpeedToPosition();    
    
  if (switch_3_1.touched()) // These are the four limit switches. If the motor wanted to move more then the bordes of the frame, the switch is pressed and stops the whole process.
  {                         // In that case, Arduino sends the number 8 to python so python will also stop and prints out the error message.
    Serial.print(8);
    exit(0);
  }
    
  if (switch_3_2.touched())
  {
    Serial.print(8);
    exit(0);
  }
    
  if (switch_6_1.touched())
  {
    Serial.print(8);
    exit(0);
  }

  if (switch_6_2.touched())
  {
    Serial.print(8);
    exit(0);
  }
  if (switch_7_2.touched())     // If the emergency button is pressed, the same thing happens. The measuring process stops.
  {
    Serial.print(9);
    exit(0);
  }
      
}

void _delay(float milliseconds){
  long endTime = millis() + milliseconds;
  while(millis() < endTime)loop();
}

// This loop is responsible for taking the measurement from the spectrum analyzer in each and every measurement point.
// When Arduino sends the number 6 to python, python writes the command to the spectrum analyzer to send the current amplitude values.
void take_a_measurement(){  
  for (int i = 0; i < measurements_in_one_point; i++) {
    _delay(time_delay_after_measurements);
    Serial.print(6);   // to take the values from the analyzer is very fast. Therefor it should first wait the sweep time and then take the measurement and move on.
  }
}

void stepper_1_movement(float step_size){  // The step size discribes the size of the step which is written in the brackets when calling this function. It moves the robot.
  stepper_1.move(step_size);
  stepper_1.setMaxSpeed(speed_of_the_motors);
  stepper_1.setSpeed(speed_of_the_motors);
}

void stepper_2_movement(float step_size){
  stepper_2.move(step_size);
  stepper_2.setMaxSpeed(speed_of_the_motors);
  stepper_2.setSpeed(speed_of_the_motors);
}

void stepper_1_movement_safety_run(float step_size){
  stepper_1.move(step_size);
  stepper_1.setMaxSpeed(speed_of_the_motors_safety_run);
  stepper_1.setSpeed(speed_of_the_motors_safety_run);
}

void stepper_2_movement_safety_run(float step_size){
  stepper_2.move(step_size);
  stepper_2.setMaxSpeed(speed_of_the_motors_safety_run);
  stepper_2.setSpeed(speed_of_the_motors_safety_run);
}

// This loop is responsible for the safety run at the beginning. It is different than the path of the real measurement because it moves with different step size depending on the size of the probe. 
// We can save time with this because if a 1mm step size is used, the satefy run does not need to use that step size but the diameter of the loop of the near-field probe.
void safety_run(){
  while(y < (number_of_steps_yaxis_safety_run))
  {
    while (x < number_of_steps_xaxis)
    {
      stepper_1_movement_safety_run(step_motor * turn);
      x += 1;
      _delay(time_of_step_safety_run);
    }
    turn = turn*(-1);
    stepper_2_movement_safety_run(-step_motor_safety_run);
    x = 0;
    _delay(time_of_step_y_safety_run);
    y += 1;
  }
    
  // The last step before the robot goes back to zero. It depends on the size of the PCB.
  
  if (number_of_steps_yaxis_safety_run % 2 == 0){     // if it is even
    while (x < number_of_steps_xaxis)
    {
      stepper_1_movement_safety_run(step_motor);
      x += 1;
      _delay(time_of_step_safety_run);
    }
    stepper_2_movement_safety_run(-((remainder/diameter_of_probe) * step_motor_safety_run)); 
    _delay(time_of_step_y_safety_run * (remainder / diameter_of_probe));
    x = 0;
    while (x < number_of_steps_xaxis)
    {
      stepper_1_movement_safety_run(-step_motor);
      x += 1;
      _delay(time_of_step_safety_run);
    }
  }
  else {
    while (x < number_of_steps_xaxis)
    {
      stepper_1_movement_safety_run(-step_motor);
      x += 1;
      _delay(time_of_step_safety_run);
    }
    stepper_2_movement_safety_run(-((remainder/diameter_of_probe) * step_motor_safety_run)); 
    _delay(time_of_step_y_safety_run * (remainder / diameter_of_probe));
    x = 0;
    while (x < number_of_steps_xaxis)
    {
      stepper_1_movement_safety_run(step_motor);
      x += 1;
      _delay(time_of_step_safety_run);
    }
  }
  _delay(time_of_step_safety_run + 1000);                     // 1000 is there so that after the neccessary part of the plotting is done, the robot waits and then goes back to zero.

  // Go back to the origin

  if (number_of_steps_yaxis_safety_run % 2 == 0)
  {
    stepper_2_movement_safety_run((number_of_steps_yaxis_safety_run + (remainder/diameter_of_probe))  * step_motor_safety_run);
    _delay(time_of_step_y_safety_run * (number_of_steps_yaxis_safety_run + (remainder / diameter_of_probe)));

  }
  else{
    stepper_2_movement_safety_run((number_of_steps_yaxis_safety_run + (remainder/diameter_of_probe))  * step_motor_safety_run);
    _delay(time_of_step_y_safety_run * (number_of_steps_yaxis_safety_run + (remainder / diameter_of_probe)));
    stepper_1_movement_safety_run(-number_of_steps_xaxis * step_motor);
    _delay(time_of_step_safety_run * number_of_steps_xaxis);   // This delay is just to wait with breaking the code until the probe is back to the origin.  
  }
}

// In this loop, Arduino reads the five neseccary input values from python and executes the initial calculations that are important for the motor control.
void input_values(){
  while(waiting_for_values==0){
    while(Serial.available()==11){
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
  string5 = String(incoming[4]);
  string6 = String(incoming[5]);
  string7 = String(incoming[6]);
  string8 = String(incoming[7]);
  string9 = String(incoming[8]);
  string10 = String(incoming[9]);
  safety_round = incoming[10];

  if(incoming[1]>9){
    string2 = "";
  }
  if(incoming[3]>9){
    string4 = "";
  }
  if(incoming[6]>9){
    string7 = "";
  }
  if(incoming[7]>9){
    string8 = "";
  }
  if(incoming[8]>9){
    string9 = "";
  }

  A_string = string1+string2;
  B_string = string3+string4;
  step_mm_string = string5;
  time_delay_after_measurements_string = string6+string7+string8+string9;
  measurements_in_one_point_string = string10;

  //---------------------------------------------------------------------------------------
  // Here comes the important calculation part. The following values will be used during the robot movement.
  A = A_string.toFloat();
  B = B_string.toFloat();
  step_mm = step_mm_string.toFloat();
  time_delay_after_measurements = time_delay_after_measurements_string.toFloat();
  measurements_in_one_point = measurements_in_one_point_string.toInt();
  

  step_motor              = (step_mm / one_revolution_mm) * one_revolution_step;  // This is the value which has to be given to the motors to run.(stepper.move() ==> command)
  time_of_a_step          = step_mm * 18.42;               // 49.01 is the time duration of one mm at 2000 speed. this is the time of moving the probe. It depends on the speed which you'd like to set.
  number_of_steps_xaxis   = (round(A / step_mm)); //This gives the number of steps on the x axis. This number is rounded.
  number_of_steps_yaxis   = (round(B / step_mm));

  // The next six variables are called to control the safety run of the robot befor the measurement.

  time_of_step_safety_run         = step_mm * 49.01; // On the x-axis I let the motor to take the same distance as it will take while the real measurement.
  time_of_step_y_safety_run       = diameter_of_probe * 49.01;  // On the y-axis it is enough to move with the diameter of the probe so we can see if the probe would collide with anything.
  step_motor_safety_run           = (diameter_of_probe / one_revolution_mm) * one_revolution_step;  // 8 is the diameter of the probe. That's the distance what the probe should go during the safety run.
  number_of_steps_yaxis_safety_run  = int((number_of_steps_yaxis * step_mm) / diameter_of_probe);
  remainder = (number_of_steps_yaxis * int(step_mm)) % diameter_of_probe;
 
}
