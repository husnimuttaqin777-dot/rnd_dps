/*
LCT AYU 48 CABLESHIP COMPASS, WIND SENSORS, and GPS COMMUNICATION
Written by : Husni and Fandi

MQTT CONNECTION to GENERATOR MAIN ENGINE POWERLINE
*/

#include<avr/wdt.h>
#include <Wire.h>
#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>

#include <TinyGPSPlus.h>
TinyGPSPlus gps;

//#include  <TimerOne.h>   
volatile int i=0;               
volatile boolean zero_cross=0;  
int AC_pin = 6;                
int alpha = 0;                                          
int freqStep = 75;    
int zc_condition;
int saturation = 128;
int alpha_buff = 125;
int wind_dir = 0;
int wind_dir_raw;
int wind_speed = 0;
int reset_pin = 7;
int wind_tick;
int wind_val_prev;
int wind_val;

unsigned long message_time;
unsigned long message_time_prev;


unsigned long time_now;
unsigned long time_elapsed;
unsigned long time_prev;

unsigned long time_send;
unsigned long time_send_prev;
int time_message = 1000;

float latitude;
float longitude;
int azimuth =0;
float knot;
float cog;

String status_compass = "magnetometer";

int val;
// Update these with values suitable for your network.
byte mac[]    = {  0x6E, 0xAD, 0xBA, 0xFE, 0xFE, 0xE6 }; 

IPAddress ip(123,45,0,103);
IPAddress server(123,45,0,10);


#include <Wire.h> //I2C Arduino Library



#define HMC5883L_ADDR 0x1E //0011110b, I2C 7bit address of HMC5883

bool haveHMC5883L = false;

int azimuth_raw;




bool detectHMC5883L (){
  // read identification registers
  Wire.beginTransmission(HMC5883L_ADDR); //open communication with HMC5883
  Wire.write(10); //select Identification register A
  Wire.endTransmission();
  Wire.requestFrom(HMC5883L_ADDR, 3);
  if(3 == Wire.available()) {
    char a = Wire.read();
    char b = Wire.read();
    char c = Wire.read();
    if(a == 'H' && b == '4' && c == '3')
      return true;
  }

  return false;
}



void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  String messageTemp;
  
  for (int i = 0; i < length; i++) {
    messageTemp += (char)message[i];
    
  }

   if (String(topic) == "mode_compass") {
   status_compass = messageTemp; 
   Serial.println(status_compass);
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
      client.subscribe("mode_compass");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(3000);
      digitalWrite(7, LOW);
    }
  } 
}



void setup() {
  pinMode (7, OUTPUT);
  digitalWrite(7, HIGH);
  Wire.begin();
  Serial.begin(115200);
  Serial2.begin(9600);
  Serial.println("booting....");
  client.setServer(server, 1883);
  client.setCallback(callback);
  
  
  
  pinMode (5, OUTPUT);
  Ethernet.begin(mac, ip);
  delay(1500);
  wdt_enable(WDTO_8S);
  TWBR = 78;  // 25 kHz 
  TWSR |= _BV (TWPS0);  // change prescaler  
// TCCR0B = 0b00000011; // x64
// TCCR0A = 0b00000011; // fast pwm
}

static char latitude_send[10];
static char longitude_send[10];
static char azimuth_send[10];
static char wind_dir_send[10];
static char wind_tick_send[10];
static char knot_send[10];

void loop() {
  time_now = millis();
  if (analogRead(A8) > 600){
    wind_val = 1;
  }
  if (analogRead(A8) < 500){
    wind_val = 0;
  }
  
  analogWrite(5, alpha);
  if (wind_val != wind_val_prev){
    wind_tick++;
  }

  while (Serial2.available() > 0)
    if (gps.encode(Serial2.read()))
      displayInfo();

  if (millis() > 5000 && gps.charsProcessed() < 10)
  {
    Serial.println(F("No GPS detected: check wiring."));

  }

  
  if (!client.connected()) {
    reconnect();
  }
  
  time_send = millis() - time_send_prev;
  if (time_send > time_message){
  
  bool detect = detectHMC5883L();

  if(!haveHMC5883L) 
  {
    if(detect) 
    {
      haveHMC5883L = true;
      Serial.println("We have HMC5883L, moving on");
      // Put the HMC5883 IC into the correct operating mode
      Wire.beginTransmission(HMC5883L_ADDR); //open communication with HMC5883
      Wire.write(0x02); //select mode register
      Wire.write(0x00); //continuous measurement mode
      Wire.endTransmission();
    }
    else
    {  
      Serial.println("No HMC5883L detected!");
      delay(2000);
      return;
    }
  }
  else
  {
    if(!detect) {
      haveHMC5883L = false;
      Serial.println("Lost connection to HMC5883L!");
      delay(2000);
      return;
    }
  }
  
  int x,y,z; //triple axis data

  //Tell the HMC5883 where to begin reading data
  Wire.beginTransmission(HMC5883L_ADDR);
  Wire.write(0x03); //select register 3, X MSB register
  Wire.endTransmission();

 //Read data from each axis, 2 registers per axis
  Wire.requestFrom(HMC5883L_ADDR, 6);
  if(6<=Wire.available()){
    x = Wire.read()<<8; //X msb
    x |= Wire.read(); //X lsb
    z = Wire.read()<<8; //Z msb
    z |= Wire.read(); //Z lsb
    y = Wire.read()<<8; //Y msb
    y |= Wire.read(); //Y lsb
  }
  
  //Print out values of each axis
  //Serial.print("x: ");
  //Serial.print(x);
  //Serial.print("  y: ");
  //Serial.print(y);


  azimuth_raw = atan2(y,x) * 180/PI;
  if (azimuth_raw < 0) {
  azimuth_raw += 360; // Jika azimuth negatif, tambahkan 360 untuk membawa nilainya ke dalam rentang 0-360 derajat.
}

  if (azimuth_raw > 0 && azimuth_raw <= 90){
    azimuth = map(azimuth_raw, 0 , 90, 127, 214);
  }

  if (azimuth_raw > 90 && azimuth_raw <= 180){
    azimuth = map(azimuth_raw, 90 , 180, 214, 259);
  }

  if (azimuth_raw > 180 && azimuth_raw <= 270){
    azimuth = map(azimuth_raw, 180 , 270, 259, 351);
  }
  if (azimuth_raw > 270 && azimuth_raw <= 360){
    azimuth = map(azimuth_raw, 270 , 360, 351, 494);
  }
  //Serial.print("  azimuth: ");
  //Serial.println(azimuth);
  
  azimuth = azimuth % 360;
  wind_dir_raw = map(analogRead(A9), 107, 879,0,270);
  if (wind_dir_raw < 0){
    wind_dir = 360 - wind_dir_raw;
  }

  if (wind_dir_raw > 0){
    wind_dir =  wind_dir_raw;
  }

  wind_dir = wind_dir % 360;
  
  
  client.publish("GPS/lat", dtostrf(latitude,6,5,latitude_send));
  client.publish("GPS/long", dtostrf(longitude,6,5,longitude_send));
  
  client.publish("winddirect", dtostrf(wind_dir,6,5,wind_dir_send));
  client.publish("system","on");
  client.publish("windspeed", dtostrf(wind_tick,6,5,wind_tick_send));
  wind_tick = 0;

  if (status_compass == "magnetometer"){
  client.publish("yaw", dtostrf(azimuth,6,5,azimuth_send));
  }

  if (status_compass == "cog"){
  client.publish("yaw", dtostrf(cog ,6,5,azimuth_send));
  }

  client.publish("speed_nmea",dtostrf(knot, 6,5,knot_send));
  
  time_send_prev = millis();
  }
  
  client.loop();
  time_elapsed = time_now - time_prev;
  time_prev = time_now;

   wdt_reset();
   wind_val_prev = wind_val;
}  


void displayInfo()
{
  Serial.print(F("Location: ")); 
  if (gps.location.isValid())
  {
    
    latitude = (gps.location.lat());
    Serial.print(latitude);
    Serial.print(F(","));
    
    longitude = (gps.location.lng());
    Serial.print(longitude);
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

  if (gps.course.isValid()){
    cog = gps.course.deg();
    //status_compass = "cog";
  }

  else{
    //status_compass = "magnetometer";
  }


  

  Serial.print(F("  Date/Time: "));
  if (gps.date.isValid())
  {
    Serial.print(gps.date.month());
    Serial.print(F("/"));
    Serial.print(gps.date.day());
    Serial.print(F("/"));
    Serial.print(gps.date.year());
  }
  else
  {
    Serial.print(F("INVALID"));
  }

  Serial.print(F(" "));
  if (gps.time.isValid())
  {
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
  }
  else
  {
    Serial.print(F("INVALID"));
  }

  Serial.println();
}
