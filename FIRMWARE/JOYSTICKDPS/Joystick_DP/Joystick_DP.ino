/*
 * linux open COM port : sudo chmod a+rw /dev/ttyACM0
 * 
 * 
 * 
 */


#include <Wire.h>
#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>


const char* speed1Publish = "speedinput1";

static char station_keeping_status_send[10];

static char speed1_out[10];
static char speed2_out[10];
static char speed3_out[10];
static char speed4_out[10];

static char speed1m_out[10];
static char speed2m_out[10];
static char speed3m_out[10];
static char speed4m_out[10];

static char speed5_out[10];
static char speed6_out[10];

static char steer1_command_send[10];
static char steer2_command_send[10];
static char steer3_command_send[10];
static char steer4_command_send[10];

char buf[10];
const char* motor1Publish = "Steering_1";
const char* motor2Publish = "Steering_2";

const char* motor3Publish = "Steering_3";
const char* motor4Publish = "Steering_4";
const char* motor5Publish = "Steering_Central Kiri";
const char* motor6Publish = "Steering_Central Kanan";


const String turn_leftID = "Kiri";
const String turn_rightID = "Kanan";
const String Hold = "Tahan";

// DP1
const int speed1PIN = A2; //A2 A3
const int button_L1 =  19;
const int button_R1 = 12;
int buttonstate1 = 0; 
int buttonstate2 = 0; 
int buttonstate1_prev = 0; 
int buttonstate2_prev = 0; 
int speed1;
int speed1_m;


//DP2
const int speed2PIN = A3; //a2  A4
const int button_L2 =  23;
const int button_R2 = 9;
int buttonstate3 = 0; 
int buttonstate4 = 0;
int buttonstate3_prev = 0; 
int buttonstate4_prev = 0;
int speed2;
int speed2_m;

//DP3
const int speed3PIN = A4; //a3 A1
const int button_L3 = 7;
const int button_R3 = 6;
int buttonstate5 = 0; 
int buttonstate6 = 0; 
int buttonstate5_prev = 0; 
int buttonstate6_prev = 0; 
int speed3;
int speed3_m;

//DP4
const int speed4PIN = A0; //a4  A2
const int button_L4 = 3;
const int button_R4 = 2;
int buttonstate7 = 0; 
int buttonstate8 = 0;
int buttonstate7_prev = 0; 
int buttonstate8_prev = 0;
int speed4;
int speed4_m;


int speed1_prev;
int speed2_prev;
int speed3_prev;
int speed4_prev;

//DP CENTRAL KANAN
const int speed5PIN = A5;
const int button_L5 = 14; 
const int button_R5 = 15;  
int buttonstate9 = 0; 
int buttonstate10 = 0; 
int speed5;


//DP CENTRAL KIRI
const int speed6PIN = A6;
const int button_L6 = 17; 
const int button_R6 = 18;  
int buttonstate11 = 0; 
int buttonstate12 = 0; 
int buttonstate10_prev;
int speed6;

unsigned long station_keeping_time;
unsigned long station_keeping_time_prev;
bool station_keeping_state;
bool station_keeping_state_prev;
bool station_keeping_status = 0;

unsigned long message_time;
unsigned long message_time_prev;

int central_status;
int central_pin = 16;

int steer1_command;
int steer2_command;
int steer3_command;
int steer4_command;


int gas_time;
int gas_time_prev;

int publish_counter;



// Update these with values suitable for your network.
byte mac[]    = {  0xDE, 0xED, 0xBA, 0xFE, 0xFE, 0xE8 };
IPAddress ip(123, 45, 0, 108);
IPAddress server(123, 45, 0, 10);

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i=0;i<length;i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}
EthernetClient ethClient;
PubSubClient client(ethClient);
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("JoystickClient")) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      //client.publish("outTopic","hello world");
      // ... and resubscribe
      client.subscribe("MainControl");
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

  pinMode(central_pin, INPUT_PULLUP);
  
  // DP1
  digitalWrite(speed1PIN, INPUT);
  digitalWrite(button_L1, INPUT_PULLUP);
  digitalWrite(button_R1, INPUT_PULLUP);
  //DP2
  digitalWrite(speed2PIN, INPUT);
  digitalWrite(button_L2, INPUT_PULLUP);
  digitalWrite(button_R2, INPUT_PULLUP);
  //DP3
  digitalWrite(speed3PIN, INPUT);
  digitalWrite (button_L3, INPUT_PULLUP);  
  digitalWrite (button_R3, INPUT_PULLUP);  

  //DP4
  digitalWrite(speed4PIN, INPUT);
  digitalWrite (button_L4, INPUT_PULLUP);  
  digitalWrite (button_R4, INPUT_PULLUP); 
  //DP CENTRAL KANAN
  digitalWrite(speed5PIN, INPUT);
  digitalWrite (button_L5,  INPUT_PULLUP);  
  digitalWrite (button_R5, INPUT_PULLUP);  
  //DP CENTRAL KIRI
  digitalWrite(speed6PIN, INPUT);
  digitalWrite (button_L6, INPUT_PULLUP);  
  digitalWrite (button_R6, INPUT_PULLUP);  

  client.setServer(server, 1883);
  client.setCallback(callback);

  Ethernet.begin(mac, ip);

  delay(1500);

 
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }

    

     buttonstate1 = digitalRead(button_L1);  // DP LCT Propeller 1
     buttonstate2 = digitalRead(button_R1);  // DP LCT Propeller 1
     
     buttonstate3 = digitalRead(button_L2);  // DP LCT Propeller 2
     buttonstate4 = digitalRead(button_R2);  // DP LCT Propeller 2

     buttonstate5 = digitalRead(button_L3);  // DP  Propeller 3
     buttonstate6 = digitalRead(button_R3);  // DP  Propeller 3
     
     buttonstate7 = digitalRead(button_L4);  // DP  Propeller 4
     buttonstate8 = digitalRead(button_R4);  // DP  Propeller 4

     
     buttonstate9 = digitalRead(button_L5);  // DP  Propeller central Kanan
     buttonstate10 = digitalRead(button_R5);  // DP  Propeller central kanan
     
     buttonstate11 = digitalRead(button_L6);  // DP  Propeller central kiri
     buttonstate12 = digitalRead(button_R6);  // DP  Propeller central kiri


  speed1 = map(analogRead(speed1PIN),0,1023,100,0);
  //speed1_m = map(speed1,0,100,132,255); //220 buat 11 V. 255 buat 12V

  speed2 = map(analogRead(speed2PIN),0,1023,100,0);
  //speed2_m = map(speed2,0,100,132,255); 

  speed3 = map(analogRead(speed3PIN),0,1023,100,0);
  //speed3_m = map(speed3,0,100,132,255); 

  speed4 = map(analogRead(speed4PIN),0,1023,100,0);
  //speed4_m = map(speed4,0,100,132,255); 

  speed5 = analogRead (speed5PIN);
  //speed5 = map(speed5,0,1023,703,388);

  speed6 = analogRead (speed6PIN);
  //speed6 = map(speed6,0,1023,703,388);

  central_status = digitalRead(central_pin);
  if (central_status == 1){
      client.publish("central_status","central");
  }

  if (central_status == 0){
      client.publish("central_status","local");
  }


// steering DP1
  if (buttonstate1_prev != buttonstate1 || buttonstate2_prev != buttonstate2){

  if (buttonstate1 == LOW)
  {
    client.publish(motor1Publish,String(turn_leftID).c_str());
  }

 

  if (buttonstate2 == LOW)
  {
    client.publish(motor1Publish,String(turn_rightID).c_str());
  }

   if (buttonstate2 == HIGH && buttonstate1 == HIGH){
    client.publish(motor1Publish,String(Hold).c_str());
    
   }

  }
  

  // steering DP2
  if (buttonstate3_prev != buttonstate3 || buttonstate4_prev != buttonstate4){
  if (buttonstate3 == LOW)
  {
    client.publish(motor2Publish,String(turn_leftID).c_str());
  }

  if (buttonstate4 == LOW)
  {
    client.publish(motor2Publish,String(turn_rightID).c_str());
  }

   if (buttonstate3 == HIGH && buttonstate4 == HIGH){
    client.publish(motor2Publish,String(Hold).c_str());
    
   }

  }



  
// steering DP3 error issue (FIXED)
if (buttonstate5_prev != buttonstate5 || buttonstate6_prev != buttonstate6){
   if (buttonstate5 == LOW)
  {

    client.publish(motor3Publish,String(turn_leftID).c_str());
  }

   if (buttonstate6 == LOW)
  {
    client.publish(motor3Publish,String(turn_rightID).c_str());
  }

  if (buttonstate5 == HIGH && buttonstate6 == HIGH){
    client.publish(motor3Publish,String(Hold).c_str());
    
   }

}






//steering DP4
if (buttonstate7_prev != buttonstate7 || buttonstate8_prev != buttonstate8){
     if (buttonstate7 == LOW)
  {

    client.publish(motor4Publish,String(turn_leftID).c_str());
  }

  if (buttonstate8 == LOW)
  {

    client.publish(motor4Publish,String(turn_rightID).c_str());
  }

    if (buttonstate7 == HIGH && buttonstate8 == HIGH){
    client.publish(motor4Publish,String(Hold).c_str());
   }

}



  //steering DP CENTRAL KANAN
     if (buttonstate9 == LOW)
  {
    client.publish(motor5Publish,String(turn_leftID).c_str());
  }

    if (buttonstate10 == LOW)
  {
    client.publish(motor5Publish,String(turn_rightID).c_str());
  }

   if (buttonstate9 == HIGH && buttonstate10 == HIGH){
    client.publish(motor5Publish,String(Hold).c_str());
    
   }



//steering DP CENTRAL KIRI 
     if (buttonstate11 == LOW)
  {
    client.publish(motor6Publish,String(turn_leftID).c_str());
  }


   if (buttonstate11 == HIGH && buttonstate12 == HIGH){
    client.publish(motor6Publish,String(Hold).c_str());
    
   }
   else{}
  client.publish("joystick_mqtt", "on");


  gas_time = millis() - gas_time_prev;
  if (gas_time > 500){
    /*
    client.publish("propeller1", dtostrf(speed1,3,0,speed1_out));
    client.publish("propeller2", dtostrf(speed2,3,0,speed2_out));
    client.publish("propeller3", dtostrf(speed3,3,0,speed3_out));
    client.publish("propeller4", dtostrf(speed4,3,0,speed4_out));
    */
    if (speed1 != speed1_prev){
    client.publish("propeller1", dtostrf(speed1,3,0,speed1_out));
    Serial.println("p1 publish");
    }

    if (speed2 != speed2_prev){
      client.publish("propeller2", dtostrf(speed2,3,0,speed2_out));
      Serial.println("p2 publish");
    }

    if (speed3 != speed3_prev){
      client.publish("propeller3", dtostrf(speed3,3,0,speed3_out));
      Serial.println("p3 publish");
    }

    if (speed4 != speed4_prev){
      client.publish("propeller4", dtostrf(speed4,3,0,speed4_out));
      Serial.println("p4 publish");
    }
    
    
  speed1_prev = speed1;
  speed2_prev = speed2;
  speed3_prev = speed3;
  speed4_prev = speed4;
    
    if (publish_counter > 14){
      client.publish("propeller1", dtostrf(speed1,3,0,speed1_out));
      client.publish("propeller2", dtostrf(speed2,3,0,speed2_out));      
      client.publish("propeller3", dtostrf(speed3,3,0,speed3_out));
      client.publish("propeller4", dtostrf(speed4,3,0,speed4_out));
      publish_counter = 0;
    }

    publish_counter = publish_counter+1;
    gas_time_prev = millis();
  
  
  }
  
  steer1_command = map(analogRead(A12),0, 1023,360,0);
  steer2_command = map(analogRead(A13),0, 1023,360,0);
  steer3_command = map(analogRead(A14),0, 1023,360,0);
  steer4_command = map(analogRead(A15),0, 1023,360,0);

  client.publish("steer1_command", dtostrf(steer1_command,3,0,steer1_command_send));
  client.publish("steer2_command", dtostrf(steer2_command,3,0,steer2_command_send));
  client.publish("steer3_command", dtostrf(steer3_command,3,0,steer3_command_send));
  client.publish("steer4_command", dtostrf(steer4_command,3,0,steer4_command_send));

  client.loop();

  station_keeping_time = millis() - station_keeping_time_prev;
  if (buttonstate10 == LOW) // station_keeping command
  {
   if (station_keeping_time > 2000){
    station_keeping_state = 1;
    if (station_keeping_state != station_keeping_state_prev){
      station_keeping_status = !station_keeping_status;
    }
   }
   
  } else {
    station_keeping_state = 0;
    station_keeping_time_prev = millis(); 
  }

  client.publish("station_keeping", dtostrf(station_keeping_status,3,0,station_keeping_status_send));

  station_keeping_state_prev = station_keeping_state;
  buttonstate10_prev = buttonstate10;
  
  
  


  buttonstate1_prev = buttonstate1;
  buttonstate2_prev = buttonstate2;
  buttonstate3_prev = buttonstate3;
  buttonstate4_prev = buttonstate4;
  buttonstate5_prev = buttonstate5;
  buttonstate6_prev = buttonstate6;
  buttonstate7_prev = buttonstate7;
  buttonstate8_prev = buttonstate8;


}
