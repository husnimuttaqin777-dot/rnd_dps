#include <AccelStepper.h>

// Define stepper motor connections and other parameters
#define STEP_PIN 44
#define DIR_PIN 45
#define EN_PIN 46
String readString;
int stepper_speed;


int counter;
int rpm;

unsigned long message_time;
unsigned long message_time_prev;

// Create an instance of the AccelStepper class
AccelStepper stepper(1, STEP_PIN, DIR_PIN); // (1: driver interface type, STEP_PIN, DIR_PIN)

void setup() {
  Serial.begin(9600);
  pinMode(EN_PIN, OUTPUT);
  // Set the maximum speed in steps per second
  stepper.setMaxSpeed(1000); // Set your desired maximum speed here
  // Set the acceleration in steps per second per second
  stepper.setAcceleration(500); // Set your desired acceleration here
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();  
    readString += c; 
    delay(2);  
  }

    if (readString.length() >0) { 
    stepper_speed  = readString.toInt();  
    
 readString=""; 
}

  message_time = millis() - message_time_prev;
if (message_time > 500){
  Serial.println(stepper_speed);
  message_time_prev = millis();
  counter = 0;
}

  if (stepper_speed == 0){
    digitalWrite(EN_PIN, HIGH);
  } else {
    digitalWrite(EN_PIN, LOW);
  }
  // Set a new target speed
  stepper.setSpeed(stepper_speed); // Set your desired speed here
  // Move the motor to the target position
  stepper.runSpeed();
}
