#include <Wire.h>

#include <SPI.h>
#include <LittleFS.h>
#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "HASAN_wifi";
const char* password = "kulonprogo";
const char* mqtt_server = "192.168.101.11";

WiFiClient espClient;
PubSubClient client(espClient);


int value = 0;


//#include  <TimerOne.h>   

unsigned long message_time;
unsigned long message_time_prev;


unsigned long time_now;
unsigned long time_elapsed;
unsigned long time_prev;

unsigned long time_send;
unsigned long time_send_prev;
int time_message = 1000;

int val;


String steering1 = "";
String steering2 = "";


#include<ModbusMaster.h>


#define MAX485_DE 14

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

int analog1_prev;
int analog2_prev;


int propeller1 = 0;
int propeller2 = 0;
int counter;

int rpm_propeller1;
int rpm_propeller2;

int lpm_propeller1;
int lpm_propeller2;

int rpm_engine;

int central_mode;

#include <Wire.h> 
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27,20,4);  // set the LCD address to 0x27 for a 16 chars and 2 line display
#define SDA_PIN 21
#define SCL_PIN 22


int zone1;
int zone2;

int zone1_prev;
int zone2_prev;

int steering1_sensor;
int steering2_sensor;

int steering1_sensor_calibrated;
int steering2_sensor_calibrated;

int steering1_offset;
int steering2_offset;


int propeller1_prev;
int propeller2_prev;


void saveConfig(float zone1, float zone2) {
  File file = LittleFS.open("/config.txt", "w");
  if (!file) {
    Serial.println("Gagal buka file untuk write");
    return;
  }

  file.printf("zone1=%.2f\n", zone1);
  file.printf("zone2=%.2f\n", zone2);

  file.close();
  Serial.println("Config tersimpan");
}


void loadConfig() {
  if (!LittleFS.exists("/config.txt")) {
    Serial.println("File tidak ada, buat default...");

    zone1 = 0;
    zone2 = 0;

    saveConfig(zone1, zone2);
    return;
  }

  File file = LittleFS.open("/config.txt", "r");
  if (!file) {
    Serial.println("Gagal buka file untuk read");
    return;
  }

  while (file.available()) {
    String line = file.readStringUntil('\n');
    line.trim();

    if (line.startsWith("zone1=")) {
      sscanf(line.c_str(), "zone1=%d", &zone1);
    } 
    else if (line.startsWith("zone2=")) {
      sscanf(line.c_str(), "zone2=%d", &zone2);
    }
  }

  file.close();

  Serial.println("Config berhasil dibaca:");
  Serial.print("zone1 = "); Serial.println(zone1);
  Serial.print("zone2 = "); Serial.println(zone2);

  zone1_prev = zone1;
  zone2_prev = zone2;
}



void callback(char* topic, byte* message, unsigned int length) {
  /*
  Serial.print("Pesan [");
  Serial.print(topic);
  Serial.print("]: ");
  */
  String messageTemp;

  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messageTemp += (char)message[i];
  }
  

  if (String(topic) == "central_mode") {
    central_mode = messageTemp.toInt();
  }

  if (String(topic) == "Steering_1") {
    steering1 = messageTemp;

    if (steering1 == "Kiri"){
    node.writeSingleCoil(1, 1);
    node.writeSingleCoil(2, 0);
    lcd.setCursor(5,3);
    lcd.print("V X");
  } 

  if (steering1 == "Tahan"){
    node.writeSingleCoil(1, 0);
    node.writeSingleCoil(2, 0);
    lcd.setCursor(5,3);
    lcd.print("X X");
  } 

  if (steering1 == "Kanan"){
    node.writeSingleCoil(1, 0);
    node.writeSingleCoil(2, 1);
    lcd.setCursor(5,3);
    lcd.print("X V");
  } 

  }

  if (String(topic) == "Steering_4") {
    steering2 = messageTemp;

    
  if (steering2 == "Kiri"){
    node.writeSingleCoil(3, 1);
    node.writeSingleCoil(4, 0);
    lcd.setCursor(9,3);
    lcd.print("V X");
  } 

  if (steering2 == "Tahan"){
    node.writeSingleCoil(3, 0);
    node.writeSingleCoil(4, 0);
    lcd.setCursor(9,3);
    lcd.print("X X");
  } 

  if (steering2 == "Kanan"){
    node.writeSingleCoil(3, 0);
    node.writeSingleCoil(4, 1);
    lcd.setCursor(9,3);
    lcd.print("X V");
  } 



  }

  if (String(topic) == "propeller1") {
    propeller1 = (messageTemp.toInt());
  }

  if (String(topic) == "propeller4") {
    propeller2 = (messageTemp.toInt());
  }


  }

// ===== Loop utama =====
unsigned long lastMsg = 0;
char analog1_send[10];
char analog2_send[10];

char steering1_sensor_send[10];
char steering2_sensor_send[10];

char counter_send[10];

char rpm_propeller1_send[10];
char rpm_propeller2_send[10];
char lpm_propeller1_send[10];
char lpm_propeller2_send[10];
char rpm_engine_send[10];

int boot;





void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("PLC3_Client")) {
      Serial.println("connected");
      client.subscribe("lamp1");    // Subskrip topik
      client.subscribe("central_mode");
      client.subscribe("Steering_1");
      client.subscribe("Steering_4");
      client.subscribe("propeller1");
      client.subscribe("propeller4");
      client.subscribe("steering1_offset");
      client.subscribe("steering4_offset");
      client.publish("system", "WT32 online");  // Kirim status online
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
      
    }
  } 
}



void setup() {
  Wire.begin();
  Serial.begin(115200);
  setup_wifi();

  if (!LittleFS.begin(true)) { 
    Serial.println("LittleFS gagal mount");
    return;
  }
  
  Serial.println("LittleFS siap");
  delay(1000);
  Serial.println("Booting WT32-ETH01 MQTT...");


  Serial.println("booting....");
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  

  delay(1500);
  Serial2Port.begin(9600, SERIAL_8N1, 16, 17); 
  
  

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
  lcd.print("     PANEL 1");

  loadConfig();
  

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


static char yaw_send[15];
void loop() {

  if (!client.connected()) {
    uint8_t result;
    result = node.writeSingleRegister(22, 100);
    Serial.println(result);
    result = node.writeSingleRegister(23, 100);
    Serial.println(result);
    node.writeSingleCoil(1, 0);
    node.writeSingleCoil(2, 0);
    node.writeSingleCoil(3, 0);
    node.writeSingleCoil(4, 0);
    node.writeSingleCoil(5, 1);
    node.writeSingleCoil(6, 1);
    lcd.setCursor(0,1);
    lcd.print("PC : X ");
    reconnect();
    


  }

  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > 500) {  
    lastMsg = now;
    lcd.setCursor(0,1);
    lcd.print("PC : V ");
    
      uint8_t result;

  // Baca HR 2 dan 3
  result = node.readHoldingRegisters(0, 10);

  if (result == node.ku8MBSuccess) {
    analog1 = map(int(node.getResponseBuffer(0)), 0, 1950, 0, 90);
    analog2 = map(int(node.getResponseBuffer(1)), 0, 1950, 0, 90);
    rpm_propeller1 = int(node.getResponseBuffer(2)); 
    rpm_propeller2 = int(node.getResponseBuffer(4)); 
    lpm_propeller1 = int(node.getResponseBuffer(6));
    lpm_propeller2 = int(node.getResponseBuffer(8)); 
    rpm_engine = int(node.getResponseBuffer(10));

    if (boot == 0){
      analog1_prev = analog1;
      analog2_prev = analog2;
      boot = 1;
    }

    if ((analog1-analog1_prev) < -45){
      zone1 = zone1 + 1;
    }

    if ((analog1-analog1_prev) > 45){
      zone1 = zone1 - 1;
    }
    if (zone1 > 3){
      zone1 = 0;
    }

    if (zone1 < 0){
      zone1 = 3;
    }


    if (zone1 == 0){
      steering1_sensor = analog1;
    }

    if (zone1 == 1){
      steering1_sensor = analog1 + 90;
    }

    if (zone1 == 2){
      steering1_sensor = analog1 + 180;
    }

    if (zone1 == 3){
      steering1_sensor = analog1 + 270;
    }


    if ((analog2-analog2_prev) < -45){
      zone2 = zone2 + 1;
    }

    if ((analog2-analog2_prev) > 45){
      zone2 = zone2 - 1;
    }
    if (zone2 > 3){
      zone2 = 0;
    }

    if (zone2 < 0){
      zone2 = 3;
    }

    if (zone2 == 0){
      steering2_sensor = analog2;
    }

    if (zone2 == 1){
      steering2_sensor = analog2 + 90;
    }

    if (zone2 == 2){
      steering2_sensor = analog2 + 180;
    }

    if (zone2 == 3){
      steering2_sensor = analog2 + 270;
    }


    if ((zone1 != zone1_prev) or (zone2 != zone2_prev)){
      saveConfig(zone1, zone2);
      Serial.print(zone1);
      Serial.print(":");
      Serial.print(zone1_prev);
      Serial.print("|");
      Serial.print(zone2);
      Serial.println(zone2_prev);
    }


    steering1_sensor_calibrated = steering1_sensor;
    steering2_sensor_calibrated = steering2_sensor;

    /*
    Serial.print("pot 1 = ");
    Serial.print(analog1);

    Serial.print(" pot2  = ");
    Serial.print(analog2);
    
    
    Serial.print(" zone1 ");
    Serial.print(zone1);

    Serial.print(" zone2 ");
    Serial.print(zone2);

    Serial.println();
    */
    
    lcd.setCursor(0,2);
    lcd.print("PLC: V ");


  } else {
    Serial.print("Read HR gagal, error = ");
    Serial.println(result);

    lcd.setCursor(0,2);
    lcd.print("PLC: X ");
  }

  if (central_mode == 1){
    node.writeSingleCoil(0, 1);
  } else {
    node.writeSingleCoil(0, 0);
  }
  if (propeller1 != propeller1_prev){
    node.writeSingleRegister(22, (100 - propeller1));
    if (propeller1 == 0){
    node.writeSingleCoil(5, 0);
  } else {
    node.writeSingleCoil(5, 1);
  }
  }
  if (propeller2 != propeller2_prev){
  node.writeSingleRegister(23, (100 - propeller2));
  
  if (propeller2 == 0){
    node.writeSingleCoil(6, 0);
  } else {
    node.writeSingleCoil(6, 1);
  }

  }
  lcd.setCursor(0,3);
  lcd.print("SSR :");

  
  lcd.setCursor(8,3);
  lcd.print("|");
  

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
  // format string (width 6, 1 decimal)
  
  char buf[32];

  snprintf(buf, sizeof(buf), "P1:%3d|P2:%3d", propeller1, propeller2);

  lcd.setCursor(7, 1);
  lcd.print(buf);


  char buf1[32];

  snprintf(buf1, sizeof(buf1), "S1:%3d|S2:%3d", steering1_sensor_calibrated, steering2_sensor_calibrated);

  lcd.setCursor(7, 2);
  lcd.print(buf1);


  client.publish("steering1_sensor",dtostrf(steering1_sensor_calibrated, 1, 2, steering1_sensor_send));
  client.publish("steering4_sensor",dtostrf(steering2_sensor_calibrated, 1, 2, steering2_sensor_send));
  client.publish("rpm_propeller1",dtostrf(rpm_propeller1, 1, 2, rpm_propeller1_send));
  client.publish("rpm_propeller4",dtostrf(rpm_propeller2, 1, 2, rpm_propeller2_send));

  client.publish("lpm_propeller1",dtostrf(lpm_propeller1, 1, 2, lpm_propeller1_send));
  client.publish("lpm_propeller4",dtostrf(lpm_propeller2, 1, 2, lpm_propeller2_send));
  
  client.publish("rpm_engine1",dtostrf(rpm_engine, 1, 2, rpm_engine_send));


    
    
  client.publish("panel1", "heartbeat");
  //Serial.println("Publish: system -> heartbeat");

  analog1_prev = analog1;
  analog2_prev = analog2;

  zone1_prev = zone1;
  zone2_prev = zone2;

  propeller1_prev = propeller1;
  propeller2_prev = propeller2;
  }

}
