#include <ETH.h>
#include <PubSubClient.h>

// ===== Konfigurasi Ethernet (WT32-ETH01 + LAN8720) =====
#define ETH_ADDR        1
#define ETH_POWER_PIN   16
#define ETH_MDC_PIN     23
#define ETH_MDIO_PIN    18
#define ETH_TYPE        ETH_PHY_LAN8720
#define ETH_CLK_MODE    ETH_CLOCK_GPIO0_IN

bool eth_connected = false;

// ===== IP Static =====
IPAddress local_IP(123, 45, 0, 101);   // IP WT32
IPAddress gateway(123, 45, 0, 1);
IPAddress subnet(255, 255, 255, 0);
IPAddress dns(8, 8, 8, 8);

// ===== MQTT Config =====
const char* mqtt_server = "123.45.0.10";  // IP PC
const int mqtt_port = 1883;
const char* mqtt_client_name = "WT32_Client_01";

WiFiClient ethClient;
PubSubClient client(ethClient);


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
int counter;

int central_mode;

#include <Wire.h> 
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27,20,4);  // set the LCD address to 0x27 for a 16 chars and 2 line display
#define SDA_PIN 33
#define SCL_PIN 32




// ===== Event handler Ethernet =====
void WiFiEvent(WiFiEvent_t event) {
  switch (event) {
    case ARDUINO_EVENT_ETH_START:
      Serial.println("Ethernet mulai...");
      ETH.setHostname("WT32-ETH01");
      break;
    case ARDUINO_EVENT_ETH_CONNECTED:
      Serial.println("Ethernet tersambung!");
      break;
    case ARDUINO_EVENT_ETH_GOT_IP:
      Serial.print("IP Address: ");
      Serial.println(ETH.localIP());
      eth_connected = true;
      break;
    case ARDUINO_EVENT_ETH_DISCONNECTED:
      Serial.println("Ethernet terputus!");
      eth_connected = false;
      break;
    default:
      break;
  }
}

// ===== Reconnect ke MQTT broker =====
void reconnect() {
  while (!eth_connected) {
    Serial.println("Menunggu koneksi Ethernet...");
    delay(1000);
  }

  while (!client.connected()) {
    Serial.print("Menyambung ke MQTT broker...");
    if (client.connect(mqtt_client_name)) {
      Serial.println("Terhubung ke MQTT!");
      client.subscribe("lamp1");    // Subskrip topik
      client.subscribe("central_mode");
      client.subscribe("steering1");
      client.subscribe("steering2");
      client.subscribe("propeller1");
      client.subscribe("propeller2");
      client.publish("system", "WT32 online");  // Kirim status online
    } else {
      Serial.print("Gagal, rc=");
      Serial.print(client.state());
      Serial.println(" coba lagi 5 detik...");
      delay(5000);
    }
  }
}

// ===== Setup =====
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Booting WT32-ETH01 MQTT...");

  pinMode(12, OUTPUT);
  digitalWrite(12, LOW);

  // Power ke PHY
  pinMode(ETH_POWER_PIN, OUTPUT);
  digitalWrite(ETH_POWER_PIN, HIGH);
  delay(100);

  WiFi.onEvent(WiFiEvent);
  ETH.begin(ETH_ADDR, ETH_POWER_PIN, ETH_MDC_PIN, ETH_MDIO_PIN, ETH_TYPE, ETH_CLK_MODE);

  // Gunakan IP statis
  ETH.config(local_IP, gateway, subnet, dns);

  // MQTT
  client.setServer(mqtt_server, mqtt_port);
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

  Wire.begin(SDA_PIN, SCL_PIN); 
  lcd.init();                      // initialize the lcd 
  lcd.init();
  // Print a message to the LCD.
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print("     WT32 Modem");


}


// ===== Callback saat MQTT menerima pesan =====
void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Pesan [");
  Serial.print(topic);
  Serial.print("]: ");
  String messageTemp;

  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messageTemp += (char)message[i];
  }
  

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



// ===== Loop utama =====
unsigned long lastMsg = 0;
char analog1_send[10];
char analog2_send[10];
char counter_send[10];


void loop() {
  if (!client.connected()) {
    reconnect();
    lcd.setCursor(0,1);
    lcd.print("     PC   : X ");

  }

  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > 500) {  
    lastMsg = now;
    lcd.setCursor(0,1);
    lcd.print("     PC   : V ");
    
      uint8_t result;

  // Baca HR 2 dan 3
  result = node.readHoldingRegisters(0, 6);

  if (result == node.ku8MBSuccess) {
    analog1 = map(int(node.getResponseBuffer(0)), 0, 4095, 0, 360);
    analog2 = map(int(node.getResponseBuffer(1)), 0, 4095, 0, 360);
    counter = int(node.getResponseBuffer(5));


    Serial.print("pot 1 = ");
    Serial.print(analog1);

    Serial.print(" pot2  = ");
    Serial.print(analog2);

    lcd.setCursor(0,2);
    lcd.print("     PLC  : V ");


  } else {
    Serial.print("Read HR gagal, error = ");
    Serial.println(result);

    lcd.setCursor(0,2);
    lcd.print("     PLC  : X ");
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
  /*
  Serial.print(" |s : ");
  Serial.print(steering1);
  Serial.print(" ,| ");
  Serial.print(steering2);

  Serial.print(" |p : ");
  Serial.print(propeller1);
  Serial.print(" ,| ");
  Serial.print(propeller2);
  Serial.println();
  */


  client.publish("steering1_sensor",dtostrf(analog1, 1, 2, analog1_send));
  client.publish("steering2_sensor",dtostrf(analog2, 1, 2, analog2_send));
  client.publish("hsc",dtostrf(counter, 1, 2, counter_send));


    
    
    
  client.publish("system", "heartbeat");
  //Serial.println("Publish: system -> heartbeat");



  }
}
