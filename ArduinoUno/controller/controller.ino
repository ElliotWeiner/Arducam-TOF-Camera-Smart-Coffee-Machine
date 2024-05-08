// Author: Elliot Weiner
// Date: 04 / 03 / 2024
// Organization: University of Rochester Electrical and Computer Engineering Department
// Description:
//   This code allows the Arduino Uno to function as a hardware controller. It takes in commands from an I2C communication channel with
//   the Raspberry Pi 4 and translates them into actual motor control. Pinouts can be derived from the following set of pin initializations.
//

#include <Wire.h>
#include <Stepper.h>

// solenoid init
const int Sol1_Pin = 4;
const int Sol2_Pin = 5;
const int Sol3_Pin = 6;
const int Sol4_Pin = 7;

// enable pin init ( for gantry system )
const int en1 = 2;
const int en2 = 3;

// limit switch init
// left
const int lim_1 = 13;
int lim_1_val = 0;
// right
const int lim_2 = 12;
int lim_2_val = 0;

// last command
int last_command;


// init stepper motors ( for gantry system )
const int stepsPerRevolution = 200;
Stepper myStepper(stepsPerRevolution, 11, 10, 9, 8);
int direction = 0;


// setup
void setup() {
  // Join I2C bus as follower
  Wire.begin(0x8);
  Wire.onReceive(receiveEvent);

  // Limit switches
  pinMode(lim_1, INPUT);
  pinMode(lim_2, INPUT);

  // Setup Solenoid Pins
  pinMode(Sol1_Pin, OUTPUT);
  pinMode(Sol2_Pin, OUTPUT);
  pinMode(Sol3_Pin, OUTPUT);
  pinMode(Sol4_Pin, OUTPUT);

  // Setup enable pins for motor
  pinMode(en1, OUTPUT);
  pinMode(en2, OUTPUT);

  // set the speed at 50 rpm:
  myStepper.setSpeed(50);
  // initialize the serial port:
  Serial.begin(9600);


}

// set stepper motor speed
void setSpeed(int dir) {
  // stop solenoid pouring
  digitalWrite(Sol1_Pin, LOW);
  digitalWrite(Sol2_Pin, LOW);
  digitalWrite(Sol3_Pin, LOW);
  digitalWrite(Sol4_Pin, LOW);

  // set direction
  // enable and disable enable pins to regulate current flow to stepper motors
  if ( dir == 1 ) {
    direction = 100;
    digitalWrite(en1, HIGH);
    digitalWrite(en2, HIGH);
  }
  else if ( dir == 2 ) {
    direction = -100;
    digitalWrite(en1, HIGH);
    digitalWrite(en2, HIGH);
  }
  else {
    direction = 0;
    digitalWrite(en1, LOW);
    digitalWrite(en2, LOW);
  }
}

// set solenoid output
void setSol(int dir) {
  // disable stepper motor
  direction = 0;
  digitalWrite(en1, LOW);
  digitalWrite(en2, LOW);

  // clear solenoid pinout
  digitalWrite(Sol1_Pin, LOW);
  digitalWrite(Sol2_Pin, LOW);
  digitalWrite(Sol3_Pin, LOW);
  digitalWrite(Sol4_Pin, LOW);

  // Enable specific solenoid
  if ( dir == 3 ) {
    digitalWrite(Sol1_Pin, HIGH);
    Serial.println(dir);
  }
  else if ( dir == 4 ) {
    digitalWrite(Sol2_Pin, HIGH);
    Serial.println(dir);
  }
  else if ( dir == 5 ) {
    digitalWrite(Sol3_Pin, HIGH);
    Serial.println(dir);
  }
  else if ( dir == 6 ) {
    digitalWrite(Sol4_Pin, HIGH);
    Serial.println(dir);
  }
}


void loop() {
  // motor step
  myStepper.step(direction);

  //set limits 
  lim_1_val = digitalRead(lim_1);
  lim_2_val = digitalRead(lim_2);
  
  // hit right
  if( lim_2_val == 1 ) {
    Serial.println("Hit right!");
    setSpeed(0);
    Serial.println("move to restart");
    moveToStart();
    Serial.println("restarted");
  }

  // if moving left, hit left
  if( last_command == 1 ) {
    if( lim_1_val == 1 ) {
    Serial.println("Hit left!");
    setSpeed(0);
    Serial.println("restarted");
  }

  }
}

// move to start position
void moveToStart() {
  setSpeed(1);
  Serial.println("restarting");
  while( lim_1_val != 1 ) {
    lim_1_val = digitalRead(lim_1);
    myStepper.step(direction);
  }
  setSpeed(0);
}

// RPi4 I2C recieve event
void receiveEvent(int howMany) {
  while (Wire.available()) {
    // get message
    int in = Wire.read();
    Serial.println(in);

    last_command = in;

    // Speed
    if (in == 0 || in == 1 || in == 2) {
      setSpeed(in);
    }
    // Pour
    else if (in == 3 || in == 4 || in == 5 || in == 6 || in == 7){
      setSol(in);
    }
  }
}