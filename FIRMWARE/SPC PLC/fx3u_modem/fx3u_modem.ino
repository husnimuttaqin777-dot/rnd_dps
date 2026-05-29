#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>


// Replace the next variables with your SSID/Password combination
const char* ssid = "HASAN_wifi";
const char* password = "kulonprogo";
const char* mqtt_server = "192.168.101.11";

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;

String steering1 = "";
String steering2 = "";


#include<ModbusMaster.h>


#define MAX485_DE 14


//DI => TX  6
//RO => RX 5
HardwareSerial Serial2Port(2); // UART2

ModbusMaster node;

void preTransmission()
{

  digitalWrite(MAX485_DE, 1);
  delay(5);
}

void postTransmission()
{

  digitalWrite(MAX485_DE, 0);
  delay(5);
}



int analog1;
int analog2;
int propeller1;
int propeller2;

int central_mode;

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  Serial2Port.begin(9600, SERIAL_8N1, 5, 17); 

  pinMode(MAX485_DE, OUTPUT);

  // Init in receive mode

  digitalWrite(MAX485_DE, 1);

  //My slave uses 9600 baud
  delay(10);
  Serial.println("starting arduino: ");
  Serial.println("setting up Serial ");
  Serial.println("setting up RS485 port ");
//  slave id
  node.begin(1, Serial2Port);
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);


}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

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

  
  if (String(topic) == "central_mode") {
    central_mode = messageTemp.toInt();
  }

  if (String(topic) == "steering1") {
    steering1 = messageTemp;
  }

  if (String(topic) == "steering2") {
    steering2 = messageTemp;
  }

  if (String(topic) == "propeller1") {
    propeller1 = messageTemp.toInt();
  }

  if (String(topic) == "propeller2") {
    propeller2 = messageTemp.toInt();
  }

  



}



void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client_dhuasdbhiadbao2379")) {
      Serial.println("connected");

      client.subscribe("central_mode");
      client.subscribe("steering1");
      client.subscribe("steering2");
      client.subscribe("propeller1");
      client.subscribe("propeller2");
      

    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}


char analog1_send[10];
char analog2_send[10];

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();


  long now = millis();
  if (now - lastMsg > 500) {
    lastMsg = now;

    uint8_t result;

  // Baca HR 2 dan 3
  result = node.readHoldingRegisters(0, 2);

  if (result == node.ku8MBSuccess) {
    analog1 = node.getResponseBuffer(0);
    analog2 = node.getResponseBuffer(1);

    Serial.print("pot 1 = ");
    Serial.print(analog1);

    Serial.print(" pot2  = ");
    Serial.print(analog2);


  } else {
    Serial.print("Read HR gagal, error = ");
    Serial.println(result);
  }

  if (central_mode == 1){
    node.writeSingleCoil(0, 1);
  } else {
    node.writeSingleCoil(0, 0);
  }

  node.writeSingleRegister(22, propeller1);
  node.writeSingleRegister(23, propeller2);

  if (steering1 == "Kiri"){
    node.writeSingleCoil(1, 1);
    node.writeSingleCoil(2, 0);
  } 

  if (steering1 == "Tahan"){
    node.writeSingleCoil(1, 0);
    node.writeSingleCoil(2, 0);
  } 

  if (steering1 == "Kanan"){
    node.writeSingleCoil(1, 0);
    node.writeSingleCoil(2, 1);
  } 

  if (steering2 == "Kiri"){
    node.writeSingleCoil(3, 1);
    node.writeSingleCoil(4, 0);
  } 

  if (steering2 == "Tahan"){
    node.writeSingleCoil(3, 0);
    node.writeSingleCoil(4, 0);
  } 

  if (steering2 == "Kanan"){
    node.writeSingleCoil(3, 0);
    node.writeSingleCoil(4, 1);
  } 

  if (propeller1 == 0){
    node.writeSingleCoil(5, 0);
  } else {
    node.writeSingleCoil(5, 1);
  }

  if (propeller2 == 0){
    node.writeSingleCoil(6, 0);
  } else {
    node.writeSingleCoil(6, 1);
  }

  Serial.print(" |s : ");
  Serial.print(steering1);
  Serial.print(" ,| ");
  Serial.print(steering2);

  Serial.print(" |p : ");
  Serial.print(propeller1);
  Serial.print(" ,| ");
  Serial.print(propeller2);
  Serial.println();



  client.publish("sensor1",dtostrf(analog1, 1, 2, analog1_send));
  client.publish("sensor2",dtostrf(analog2, 1, 2, analog2_send));


  }
}
