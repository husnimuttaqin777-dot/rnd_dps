#include<avr/wdt.h>

#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>

#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>

byte mac[]    = {  0xDE, 0xED, 0xBA, 0xF1, 0xFE, 0xE6 }; 

IPAddress ip(123,45,0,104);
IPAddress server(123,45,0,10);

// The TinyGPSPlus object
TinyGPSPlus gps;


#include<ModbusMaster.h>


#define MAX485_DE 23
#define MAX485_RE_NEG 25

//DI => TX
//RO => RX


ModbusMaster node;

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_HMC5883_U.h>

float heading_calibrated;
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

int cog;

int precision_scale = 1;

float knot;

unsigned long time_send;
unsigned long time_send_prev;


float windspeed;
int wind_direction;

void displaySensorDetails(void)
{
  sensor_t sensor;
  mag.getSensor(&sensor);
  Serial.println("------------------------------------");
  Serial.print  ("Sensor:       "); Serial.println(sensor.name);
  Serial.print  ("Driver Ver:   "); Serial.println(sensor.version);
  Serial.print  ("Unique ID:    "); Serial.println(sensor.sensor_id);
  Serial.print  ("Max Value:    "); Serial.print(sensor.max_value); Serial.println(" uT");
  Serial.print  ("Min Value:    "); Serial.print(sensor.min_value); Serial.println(" uT");
  Serial.print  ("Resolution:   "); Serial.print(sensor.resolution); Serial.println(" uT");  
  Serial.println("------------------------------------");
  Serial.println("");
  delay(500);
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

  /* Initialise the sensor */
  if(!mag.begin())
  {
    /* There was a problem detecting the HMC5883 ... check your connections */
    Serial.println("Ooops, no HMC5883 detected ... Check your wiring!");
    while(1);
  }
  
  /* Display some basic information on this sensor */
  displaySensorDetails();


  Serial1.begin(9600);
  Serial.begin(115200);
  Serial2.begin(4800);

  pinMode(MAX485_RE_NEG, OUTPUT);
  pinMode(MAX485_DE, OUTPUT);

  // Init in receive mode
  digitalWrite(MAX485_RE_NEG, 1);
  digitalWrite(MAX485_DE, 1);

  Serial.println("starting arduino: ");
  Serial.println("setting up Serial ");
  Serial.println("setting up RS485 port ");
  // slave id
  node.begin(1, Serial2);
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);

  
  



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

static char cog_send[15];


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
  heading_calibrated = (-0.0013827750110249715 * pow(headingDegrees, 2))  + (-0.6314639481776498 * headingDegrees) + 249.57563928260194;

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
      
      //Serial.print("Register ");
      //Serial.print(i);
      //Serial.print(": ");
      //Serial.println(data[i]);
      
      }
    }
  } else {
    //Serial.println("Failed to read holding registers!");
  }
  
  // This sketch displays information every time a new sentence is correctly encoded.
  while (Serial1.available() > 0)
    if (gps.encode(Serial1.read()))
      displayInfo();

  time_send = millis() - time_send_prev;
  if (time_send > 500){

    /*
    Serial.print(gps.location.lat(), 9);
    Serial.print(F(","));
    Serial.print(gps.location.lng(), 9);
    Serial.println();
    */
    Serial.print(headingDegrees);
    Serial.print(" deg");
   Serial.println();
  // Gunakan dtostrf untuk konversi dengan presisi 9 angka di belakang kom

    client.publish("latitude_aux",dtostrf(latitude,12,9,latitude_send));
    client.publish("longitude_aux",dtostrf(longitude,12,9,longitude_send));

    
    //client.publish("lat_nmea",dtostrf(latitude,12,9,latitude_send));
    //client.publish("long_nmea",dtostrf(longitude,12,9,longitude_send));
    client.publish("speed_nmea",dtostrf(knot,7,3,knot_send));
    client.publish("windspeed",dtostrf(windspeed,7,1,windspeed_send));
    client.publish("winddirect",dtostrf(wind_direction,7,1,wind_direction_send));
    client.publish("yaw_actual",dtostrf(heading_calibrated,6,0,yaw_send));
    client.publish("cog", dtostrf(cog, 7,3,cog_send));
    time_send_prev = millis();
  }

  wdt_reset();
}

void displayInfo()
{
  if (gps.location.isValid())
  {
    latitude = gps.location.lat();
    longitude = gps.location.lng();
    
   
  }

  if (gps.course.isUpdated()) {
      cog = gps.course.deg();
    }

    
  else
  {
    Serial.print(F("INVALID"));
  }

  if (gps.date.isValid())
  {
    /*
    Serial.print(gps.date.month());
    Serial.print(F("/"));
    Serial.print(gps.date.day());
    Serial.print(F("/"));
    Serial.print(gps.date.year());
    */
  }
  else
  {
    Serial.print(F("INVALID"));
  }

  Serial.print(F(" "));
  if (gps.time.isValid())
  {
    /*
    if (gps.time.hour() < 10) Serial.print(F("0"));
    Serial.print(gps.time.hour());
    Serial.print(F(":"));
    if (gps.time.minute() < 10) Serial.print(F("0"));
    Serial.print(gps.time.minute());
    Serial.print(F(":"));
    if (gps.time.second() < 10) Serial.print(F("0"));
    Serial.print(gps.time.second());
    Serial.print(F("."));
    if (gps.time.centisecond() < 10) Serial.print(F("0"));
    Serial.print(gps.time.centisecond());
    */
  }
  else
  {
    Serial.print(F("INVALID"));
  }

  if(gps.speed.isValid()){
    knot = gps.speed.kmph() * 0.539957;
  } else {
    knot = 0;
  }

  
}
