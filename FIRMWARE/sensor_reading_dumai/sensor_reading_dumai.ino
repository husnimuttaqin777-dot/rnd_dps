#include<avr/wdt.h>
#include <SoftwareSerial.h>

#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>

byte mac[]    = {  0xDE, 0xED, 0xBA, 0xF1, 0xFE, 0xE6 }; 

IPAddress ip(123,45,0,104);
IPAddress server(123,45,0,10);



#include<ModbusMaster.h>
#define RX_PIN 6
#define TX_PIN 5

SoftwareSerial mySerial(RX_PIN, TX_PIN);

#define MAX485_DE 4


//DI => TX
//RO => RX


ModbusMaster node;

#include <Wire.h>

void preTransmission()
{
  digitalWrite(MAX485_DE, 1);
  
}

void postTransmission()
{
  digitalWrite(MAX485_DE, 0);

}

// The serial connection to the GPS device



int cog;

int precision_scale = 1;

float knot;

unsigned long time_send;
unsigned long time_send_prev;


float windspeed;
int wind_direction;





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

  Serial.begin(115200);
  mySerial.begin(4800);

  pinMode(MAX485_DE, OUTPUT);

  // Init in receive mode

  digitalWrite(MAX485_DE, 1);

  Serial.println("starting arduino: ");
  Serial.println("setting up Serial ");
  Serial.println("setting up RS485 port ");
  // slave id
  node.begin(1, mySerial);
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);

  client.setServer(server, 1883);
  client.setCallback(callback);

  Ethernet.begin(mac, ip);
  delay(1500);
  wdt_enable(WDTO_8S);
}



void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  String messageTemp;
  
  for (int i = 0; i < length; i++) {
    messageTemp += (char)message[i];
    
  }

}

static char windspeed_send[15];
static char wind_direction_send[15];

static char yaw_send[15];
void loop(){
  if (!client.connected()) {
    reconnect();
  }


  wind_direction = (map(analogRead(A0), 0, 1023, 0, 360));

  
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
      Serial.println(windspeed);      

      }
    }
  } else {
    Serial.println("Failed to read holding registers!");
  }

  time_send = millis() - time_send_prev;
  if (time_send > 500){
    client.publish("windspeed",dtostrf(windspeed,7,1,windspeed_send));
    client.publish("winddirect",dtostrf(wind_direction,7,1,wind_direction_send));

    time_send_prev = millis();
  }

  wdt_reset();
}
