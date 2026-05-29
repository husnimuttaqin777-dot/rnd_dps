#include <WiFiS3.h>
#include <PubSubClient.h>
#include <SoftwareSerial.h>
#include <Wire.h>

// Konfigurasi Wi-Fi
const char* ssid = "ERA_BARU_2025";
const char* password = "Bandung888@";

// Konfigurasi MQTT
const char* mqtt_server = "172.30.1.34"; // Ganti dengan broker MQTT Anda
const int mqtt_port = 1883;
const char* mqtt_user = "username"; // Jika diperlukan
const char* mqtt_password = "password"; // Jika diperlukan

WiFiClient espClient;
PubSubClient client(espClient);

// IP Manual
IPAddress local_IP(172, 30, 1, 40);  // IP statis yang ingin Anda gunakan
//IPAddress gateway(192, 168, 1, 1);     // Gateway Anda
IPAddress subnet(255, 255, 255, 0);    // Subnet mask


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

long lastMsg = 0;
int analog;
int windspeed;
int wind_direction;



#include <Wire.h>

#include <Adafruit_Sensor.h>
#include <Adafruit_HMC5883_U.h>

int heading_calibrated;
Adafruit_HMC5883_Unified mag = Adafruit_HMC5883_Unified(12345);


void displaySensorDetails(){
  sensor_t sensor;
  mag.getSensor(&sensor);

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

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Serial1.begin(4800);

  pinMode(MAX485_RE_NEG, OUTPUT);
  pinMode(MAX485_DE, OUTPUT);

  // Init in receive mode
  digitalWrite(MAX485_RE_NEG, 1);
  digitalWrite(MAX485_DE, 1);

  Serial.println("starting arduino: ");
  Serial.println("setting up Serial ");
  Serial.println("setting up RS485 port ");

  node.begin(1, Serial1);
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);

  
  pinMode(13,OUTPUT);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Menghubungkan ke ");
  Serial.println(ssid);

  WiFi.config(local_IP, subnet);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi terhubung");
  Serial.println("Alamat IP: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Pesan diterima [");
  Serial.print(topic);
  Serial.print("] ");
  String messageTemp;

  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messageTemp += (char)message[i];
  }
  Serial.println();
  if (String(topic) == "lamp") {
    Serial.print("Changing output to ");
    if(messageTemp == "on"){
      Serial.println("ON");
      digitalWrite(13, HIGH);
    }
    else if(messageTemp == "off"){
      Serial.println("OFF");
      digitalWrite(13, LOW);
    }
  }


}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Menghubungkan ke MQTT...");
    if (client.connect("ArduinoClient")) {
      Serial.println("terhubung");
      Serial.println("Alamat IP: ");
      Serial.println(WiFi.localIP());
      client.subscribe("lamp");
    } else {
      Serial.print("gagal, rc=");
      Serial.print(client.state());
      Serial.println(" coba lagi dalam 5 detik");
      delay(5000);
    }
  }
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

void loop() {
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
  
  long now = millis();
  if (now - lastMsg > 1000) {
    lastMsg = now;
    
    //kirim data 
    analog = analogRead(A0);   
    char analog_send[8];
    dtostrf(analog, 1, 2, analog_send);
    
    client.publish("potensiometer", analog_send);
    //client.publish("windspeed",dtostrf(windspeed,7,1,windspeed_send));
    client.publish("winddirect",dtostrf(wind_direction,7,1,wind_direction_send));
    client.publish("yaw_actual",dtostrf(heading_calibrated,6,0,yaw_send));

  }


  client.loop();
  // Tambahkan logika tambahan di sini
}
