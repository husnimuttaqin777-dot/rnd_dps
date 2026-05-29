#include<avr/wdt.h>

#include <SoftwareSerial.h>

#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>

byte mac[]    = {  0xDE, 0xED, 0xBA, 0xF1, 0xFE, 0xE6 }; 

IPAddress ip(123,45,0,104);
IPAddress server(123,45,0,11);


#include<ModbusMaster.h>
const byte rxPin = 5;
const byte txPin = 6;

// Set up a new SoftwareSerial object
SoftwareSerial mySerial(rxPin, txPin);

#define MAX485_DE 3
#define MAX485_RE_NEG 2

//DI => TX
//RO => RX


ModbusMaster node;

#include <Wire.h>

#include <Adafruit_Sensor.h>
#include <Adafruit_HMC5883_U.h>

int heading_calibrated;
/* Assign a unique ID to this sensor at the same time */
Adafruit_HMC5883_Unified mag = Adafruit_HMC5883_Unified(12345);


int yaw;

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

// The serial connection to the GPS device

float latitude;
int latitude_integer;
float latitude_fractional;

float longitude;
int longitude_integer;
float longitude_fractional;

int precision_scale = 1;

float knot;

unsigned long time_send;
unsigned long time_send_prev;


float windspeed;
int wind_direction;

void displaySensorDetails(){
  sensor_t sensor;
  mag.getSensor(&sensor);

}

void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  String messageTemp;
  
  for (int i = 0; i < length; i++) {
    messageTemp += (char)message[i];
    
  }

 messageTemp ="";
}

EthernetClient ethClient;
PubSubClient client(ethClient);
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("GPS_Client")) {
      Serial.println("connected");
      
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);

    }
  } 
}


void setup(){
  Wire.begin();
  mySerial.begin(4800);

  pinMode(MAX485_RE_NEG, OUTPUT);
  pinMode(MAX485_DE, OUTPUT);

  // Init in receive mode
  digitalWrite(MAX485_RE_NEG, 1);
  digitalWrite(MAX485_DE, 1);

  Serial.println("starting arduino: ");
  Serial.println("setting up Serial ");
  Serial.println("setting up RS485 port ");
  // slave id
  
  node.begin(1, mySerial);
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);

  
  Serial.begin(115200);
  //Serial2.begin(9600);



  client.setServer(server, 1883);
  client.setCallback(callback);

  Ethernet.begin(mac, ip);
  delay(1500);
  wdt_enable(WDTO_8S);
}


static char latitude_send[40];
static char longitude_send[40];
static char knot_send[15];
static char windspeed_send[15];
static char wind_direction_send[15];

static char latitude_integer_send[15];
static char longitude_integer_send[15];

static char latitude_fractional_send[15];
static char longitude_fractional_send[15];
static char yaw_send[15];
void loop(){
  if (!client.connected()) {
    reconnect();
  }


  sensors_event_t event; 
  mag.getEvent(&event);

  float heading = atan2(event.magnetic.y, event.magnetic.x);

  float declinationAngle = 0.22;
  heading += declinationAngle;

  if(heading < 0)
    heading += 2*PI;

  if(heading > 2*PI)
    heading -= 2*PI;

  float headingDegrees = (heading * 180/M_PI); 
  heading_calibrated = (360 - (heading * 180/M_PI))-60;
  if (heading_calibrated < 0){
    heading_calibrated = 360 + heading_calibrated;
  }

  wind_direction = (map(analogRead(A0), 0, 1023, 0, 360)- 60) % 360;
  if (wind_direction < 0){
    wind_direction = 360 + wind_direction;
  }

  
  
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
      /*
      Serial.print("Register ");
      Serial.print(i);
      Serial.print(": ");
      Serial.println(data[i]);
      */
      }
    }
  } else {
    Serial.println("Failed to read holding registers!");
  }
  

  
  time_send = millis() - time_send_prev;
  if (time_send > 500){



    Serial.print(windspeed);
    Serial.print(" knot");
   Serial.println();

    client.publish("windspeed",dtostrf(windspeed,7,1,windspeed_send));
    client.publish("winddirect",dtostrf(wind_direction,7,1,wind_direction_send));
    client.publish("yaw_actual",dtostrf(heading_calibrated,6,0,yaw_send));
    time_send_prev = millis();
  }

  wdt_reset();
}
