#include<avr/wdt.h>


#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>
#include <AccelStepper.h>
#include "ESC.h"
#include <Servo.h>


#include<ModbusMaster.h>
#define MAX485_DE 3
#define MAX485_RE_NEG 2

//DI => TX
//RO => RX


ModbusMaster node;

//#include <TinyGPSPlus.h>
//TinyGPSPlus gps;
 

//DI => TX
//RO => RX
int reset_pin = 7;

int status_pin = 31;
int buzzer_pin = 32;

unsigned long message_time;
unsigned long message_time_prev;

unsigned long time_now;
unsigned long time_elapsed;
unsigned long time_prev;

unsigned long time_send;
unsigned long time_send_prev;
int time_message = 1000;

Servo servo_steering1;
Servo servo_steering2;
Servo servo_steering3;
Servo servo_steering4;


//int yaw;
float latitude;
float longitude;
float knot;

float steering1_position;
float steering2_position;
float steering3_position;
float steering4_position;

float steering1_position_filtered;
float steering2_position_filtered;
float steering3_position_filtered;
float steering4_position_filtered;

// ESC FR 
ESC propeller1 (4, 1000, 2000, 500); 
ESC propeller2 (11, 1000, 2000, 500); 

// ESC FR Manual
ESC propeller3 (8, 1000, 2000, 500);
ESC propeller4 (9, 1000, 2000, 500);

/*
  servo_steering1.attach(26);
  servo_steering2.attach(32);
  servo_steering3.attach(40);
  servo_steering4.attach(30);
*/

///////////////////////////////////


int propeller1_speed = 1000;
int propeller2_speed = 1000;
int propeller3_speed = 1000;
int propeller4_speed = 1000;

int propeller1_speed_filtered = 1000;
int propeller2_speed_filtered = 1000;
int propeller3_speed_filtered = 1000;
int propeller4_speed_filtered = 1000;

int steering1_sensor;
int steering2_sensor;
int steering3_sensor;
int steering4_sensor;

int wind_speed;

float pitch;
float roll;

// Update these with values suitable for your network.
byte mac[]    = {  0xDE, 0xED, 0xBA, 0xFE, 0xFE, 0xE6 }; 

IPAddress ip(123,45,0,103);
IPAddress server(123,45,0,15);





void callback(char* topic, byte* message, unsigned int length) {
  //Serial.print("Message arrived [");
  //Serial.print(topic);
  //Serial.print("] ");
  
  String messageTemp;
  
  for (int i = 0; i < length; i++) {
    messageTemp += (char)message[i];
    
  }

   if (String(topic) == "steering1") {
    steering1_position = (messageTemp.toInt() /2) *0.8;
   if (steering1_position < 0){
    steering1_position = (180 + (messageTemp.toInt())/2) *0.82;
   }
   //Serial.println(messageTemp.toInt());
   }

   if (String(topic) == "steering2") {
    steering2_position = (messageTemp.toInt()/2) *0.8;
   if (steering2_position < 0){
    steering2_position = (180 + messageTemp.toInt()/2) *0.84;
   }
   //Serial.println(messageTemp.toInt());
   }

   if (String(topic) == "steering3") {
    steering3_position = (messageTemp.toInt()/2) *0.8;
   if (steering3_position < 0){
    steering3_position = (180 + messageTemp.toInt()/2) *0.84;
   }
   //Serial.println(messageTemp.toInt());
   }

   if (String(topic) == "steering4") {
    steering4_position = (messageTemp.toInt()/2) *0.8;
   if (steering4_position < 0){
    steering4_position = (180 + messageTemp.toInt()/2) *0.8;
   }
   //Serial.println(messageTemp.toInt());
   }

   if (String(topic) == "propeller1") {
    if (messageTemp.toInt() == 0){
      propeller1_speed = 1000;
    } else {
      propeller1_speed = map(messageTemp.toInt(), 0, 100, 1200, 1400);
    } 
   
   //Serial.println(messageTemp.toInt());
   }

   if (String(topic) == "propeller2") {
   propeller2_speed = map(messageTemp.toInt(), 0, 100, 1000, 1130);

   //Serial.println(messageTemp.toInt());
   }
   
   if (String(topic) == "propeller3") {
    if (messageTemp.toInt() == 0){
      propeller3_speed = 1000;
    } else {
      propeller3_speed = map(messageTemp.toInt(), 0, 100, 1160, 1250);
    }
    
   //Serial.println(messageTemp.toInt());
   }
   

   if (String(topic) == "propeller4") {
    if (messageTemp.toInt() == 0){
      propeller4_speed = 1000;
    } else {
    propeller4_speed = map(messageTemp.toInt(), 0, 100, 1150, 1250);
    }
    
  
   //Serial.println(messageTemp.toInt());
   }

   if (String(topic) == "buzzer") {
     if (messageTemp == "high"){
       digitalWrite(buzzer_pin, HIGH);
     }
  
     if (messageTemp == "low"){
       digitalWrite(buzzer_pin, LOW);
     }
   }
 messageTemp ="";
}

void preTransmission()
{
  digitalWrite(MAX485_RE_NEG, 1);
  digitalWrite(MAX485_DE, 1);
}

void postTransmission()
{
  digitalWrite(MAX485_RE_NEG, 0);
  digitalWrite(MAX485_DE, 0);
}


float windspeed;

EthernetClient ethClient;
PubSubClient client(ethClient);
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("test_component")) {
      Serial.println("connected");
      client.subscribe("steering1");
      client.subscribe("steering2");
      client.subscribe("steering3");
      client.subscribe("steering4");
      client.subscribe("propeller1");
      client.subscribe("propeller2");
      client.subscribe("propeller3");
      client.subscribe("propeller4");
      client.subscribe("buzzer");
      
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
      digitalWrite(reset_pin, HIGH);
    }
  } 
}



void setup() {
  pinMode(buzzer_pin, OUTPUT);
  pinMode(status_pin, OUTPUT);

  
  Serial.begin(115200);
  Serial1.begin(4800);
    pinMode(MAX485_RE_NEG, OUTPUT);
  pinMode(MAX485_DE, OUTPUT);

  // Init in receive mode
  digitalWrite(MAX485_RE_NEG, 1);
  digitalWrite(MAX485_DE, 1);

  Serial.println("starting arduino: ");
  Serial.println("setting up Serial ");
  Serial.println("setting up RS485 port ");
  // slave id
  
  node.begin(1, Serial1);
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);

  //Serial2.begin(9600);

  Serial.println("booting....");
  client.setServer(server, 1883);
  client.setCallback(callback);

  propeller1.arm(); 
  propeller2.arm(); 
  propeller3.arm(); 
  propeller4.arm(); 
  
  servo_steering1.attach(28);
  servo_steering2.attach(32);
  servo_steering3.attach(40);
  servo_steering4.attach(30);

  Ethernet.begin(mac, ip);
  delay(1500);
  wdt_enable(WDTO_8S);
}


//static char yaw_send[15];
static char latitude_send[15];
static char longitude_send[15];
static char knot_send[15];
static char steering4_sensor_send[15];
static char wind_speed_send[15];
static char pitch_send[15];
static char roll_send[15];
static char windspeed_send[15];

void loop() {

  time_now = millis();
  if (!client.connected()) {
    digitalWrite(status_pin, LOW);
    reconnect();
  } else {
    digitalWrite(status_pin, HIGH);
  }

  /*
  int result;
  uint16_t data[10]; // Array to store the read data
  
  // Read holding registers starting from address 0, read 10 registers
  result = node.readHoldingRegisters(0, 10);
 
  // Check if the read operation was successful
  if (result == node.ku8MBSuccess) {
    // Print each register value
    for (int i = 0; i < 10; i++) {
      data[i] = node.getResponseBuffer(i); // Get the value of each register
      if(i==0){ 
      windspeed = data[i];
      
      Serial.print("Register ");
      Serial.print(i);
      Serial.print(": ");
      Serial.println(data[i]);
      
      }
    }
  } else {
    Serial.println("Failed to read holding registers!");
  }
  */
  
  

  time_send = millis() - time_send_prev;
  if (time_send > time_message){
  
  Serial.print("Steering : ");
  Serial.print(" ");
  Serial.print(steering1_position);
  Serial.print(" ");
  Serial.print(steering2_position);
  Serial.print(" ");
  Serial.print(steering3_position);
  Serial.print(" ");
  Serial.print(steering4_position);
  Serial.println();

  Serial.print("Propeller : ");
  Serial.print(" ");
  Serial.print(propeller1_speed_filtered);
  Serial.print(" ");
  Serial.print(propeller2_speed_filtered);
  Serial.print(" ");
  Serial.print(propeller3_speed_filtered);
  Serial.print(" ");
  Serial.print(propeller4_speed_filtered);
  Serial.println();

  client.publish("system","on");
  
  client.publish("pitch",dtostrf(pitch,7,0,pitch_send));
  client.publish("roll",dtostrf(roll,7,0,roll_send));
  client.publish("speed_nmea",dtostrf(knot,6,0,knot_send));

  time_send_prev = millis();
  
  }


  
  steering1_position_filtered = (0.9 * steering1_position) + (0.1 * steering1_position_filtered);
  steering2_position_filtered = (0.9 * steering2_position) + (0.1 * steering2_position_filtered);
  steering3_position_filtered = (0.9 * steering3_position) + (0.1 * steering3_position_filtered);
  steering4_position_filtered = (0.9 * steering4_position) + (0.1 * steering4_position_filtered);

  servo_steering1.write(steering1_position_filtered);
  servo_steering2.write(steering2_position_filtered);
  servo_steering3.write(steering3_position_filtered);
  servo_steering4.write(steering4_position_filtered);


 
  // ---- ESC Speed------ //
  //esc 1
  propeller1_speed_filtered = (0.5 * propeller1_speed) + (0.5 * propeller1_speed_filtered);
  propeller1.speed(propeller1_speed_filtered);
  
  //esc2
  propeller2_speed_filtered = (0.5 * propeller2_speed) + (0.5 * propeller2_speed_filtered);
  propeller2.speed(propeller2_speed_filtered);
  
  //esc 3
  propeller3_speed_filtered = (0.5 * propeller3_speed) + (0.5 * propeller3_speed_filtered);
  propeller3.speed(propeller3_speed_filtered);

  //esc 4
  propeller4_speed_filtered = (0.5 * propeller4_speed) + (0.5 * propeller4_speed_filtered);
  propeller4.speed(propeller4_speed_filtered);
  

  client.loop();
  time_elapsed = time_now - time_prev;
  time_prev = time_now;


  wdt_reset();
}  
