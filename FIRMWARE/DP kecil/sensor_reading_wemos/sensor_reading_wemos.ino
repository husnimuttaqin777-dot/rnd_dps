#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>

#include <SoftwareSerial.h>


SoftwareSerial mySerial(D5, D6); //rxPin, txPin
#include <ModbusMaster.h>
ModbusMaster node;

#define MAX485_DE 16
#define MAX485_RE_NEG 13

//DI => TX
//RO => RX

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

// Replace the next variables with your SSID/Password combination
const char* ssid = "Syergie_DPS";
const char* password = "syergie123";
const char* mqtt_server = "123.45.0.15";

WiFiClient espClient;
PubSubClient client(espClient);

// IP Manual
IPAddress local_IP(123, 45, 0, 20);  // IP statis yang ingin Anda gunakan
IPAddress gateway(0, 0, 0, 0);  // Gateway Anda
IPAddress subnet(255, 0, 0, 0);    // Subnet mask


long lastMsg = 0;
char msg[50];
int value = 0;


int windspeed;


void setup() {
  Wire.begin();
  mySerial.begin(4800);

  pinMode(MAX485_RE_NEG, OUTPUT);
  pinMode(MAX485_DE, OUTPUT);

  // Init in receive mode
  digitalWrite(MAX485_RE_NEG, 1);
  digitalWrite(MAX485_DE, 1);

  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  node.begin(1, mySerial);
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);


}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  
  // Set static IP address, gateway, and subnet mask
  WiFi.config(local_IP, gateway, subnet);  // Make sure you pass the correct gateway and subnet

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messageTemp;
  
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messageTemp += (char)message[i];
  }
  Serial.println();

  if (String(topic) == "power") {
    //power = messageTemp.toInt();

  }

}



void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("DPSENSOR")) {
      Serial.println("connected");

      client.subscribe("power");

    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}


void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();


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
      if (i == 0){
          Serial.print("wind : ");
          windspeed = data[i];
          Serial.println(windspeed);
      }
      
      
      
      Serial.print("Register ");
      Serial.print(i);
      Serial.print(": ");
      Serial.println(data[i]);
      
      }
    
  } else {
    Serial.println("Failed to read holding registers!");
  }
  */

  long now = millis();
  if (now - lastMsg > 1000) {
    lastMsg = now;
    
    //kirim data  
    char windspeed_send[8];
    char yaw_send[8];
    client.publish("windspeed",dtostrf(windspeed,7,1,windspeed_send));
    client.publish("yaw_actual",dtostrf(heading_calibrated,6,0,yaw_send));

  }
}
