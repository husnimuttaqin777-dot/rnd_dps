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
#include <avr/wdt.h>


#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27, 20, 4);  

#define SLIDER (A2) 
#define propeller1 (2)
#define propeller2 (3)
//#define propeller3 (10)
//#define propeller4 (9)


int Propeller1 = 0;

int pwm1  = 132;
int pwm2 = 132;
int pwm3 = 132;
int pwm4 = 132;

int pwm1_buffer;
int pwm2_buffer;
int pwm3_buffer;
int pwm4_buffer;


int steering1;
int steering2;
int steering3;
int steering4;



int speed_motor;

int reset_pin = 7;


unsigned long rpmtime;
float rpmfloat;
unsigned int rpm;

unsigned int rpm2;
unsigned int rpm2_filtered;

bool tooslow = 1;

unsigned long Time;
unsigned long elapsed_time;
unsigned long prev_time;

unsigned long message_time;
unsigned long prev_message_time;

unsigned long rpm_time;
unsigned long prev_rpm_time;

int tick1;
int tick2;
int tick3;
int tick4;

float rpm_filtered;

int steer1_command;
int steer2_command;
int steer3_command;
int steer4_command;

int steer1_error;
int steer2_error;
int steer3_error;
int steer4_error;

#define button_L (31)
#define button_R (33)
//#define button_mode_central (23)
#define button_mode_local (11)

int buttonstate_L = 0;
int buttonstate_R = 0;
int buttonstate_M = 0;

#define steering1_L (5)
#define steering1_R (4)

#define steering2_L (7)
#define steering2_R (6)

#define steering3_L (8)
#define steering3_R (9)

#define steering4_L (35)
#define steering4_R (37)

int propeller_select1 = 27;
int propeller_select2 = 29;


EthernetClient ethClient;
PubSubClient client(ethClient);


// Update these with values suitable for your network.
byte mac[]    = {  0xDE, 0xED, 0xBA, 0xFE, 0xFE, 0xE1 };
IPAddress ip(123, 45, 0, 101);
IPAddress server(123, 45, 0, 10);


int mode_state;
int mode_state_prev;


float flow_tick;
float flow_lpm;
float float_lpm_filtered;
int flow_state;

float flow_tick2;
float flow_lpm2;
float float_lpm_filtered2;
int flow_state2;


unsigned long flow_time;
unsigned long flow_time_prev;
unsigned long up_millis;
int flow_state_prev;
int flow_state_prev2;


String central_status; 

unsigned long time_loop;
unsigned long time_loop_prev;



float shortest_psi(float psi_ref, float psi_d) {
  float psi_temp = fmod((psi_ref - psi_d), 360.0);
  if (psi_temp < 0) {
    psi_temp += 360.0;
  }

  float psi_shortest = fmod((psi_temp + 360.0) * -1.0, 360.0);
  if (psi_shortest < 0) {
    psi_shortest += 360.0;
  }

  if (psi_shortest > 180.0) {
    psi_shortest -= 360.0;
  }

  return psi_shortest;
}




void callback(char* topic, byte* message, unsigned int length) {
  //Serial.print("Message arrived [");
  //Serial.print(topic);
  //Serial.print("] ");
  String messageTemp;
  
  for (int i=0;i<length;i++) {

    //Serial.print((char)payload[i]);
   messageTemp += (char)message[i];
  }
  

  
  //Serial.println();
if (String(topic) == "propeller1") {
     pwm1_buffer = map(messageTemp.toInt(), 0, 100, 0, 255); 
     messageTemp ="";
   }


if (String(topic) == "propeller2") {
     pwm2_buffer = map(messageTemp.toInt(), 0, 100, 0, 255); 
     messageTemp ="";
   }

if (String(topic) == "steer1_command") {
  steer1_command = messageTemp.toInt();
  messageTemp ="";
}

if (String(topic) == "steer2_command") {
  steer2_command = messageTemp.toInt();
  messageTemp ="";
}

if (String(topic) == "steer3_command") {
  steer3_command = messageTemp.toInt();
  messageTemp ="";
}

if (String(topic) == "steer4_command") {
  steer4_command = messageTemp.toInt();
  messageTemp ="";
}


if (String(topic) == "Steering_DP 1") {
  if (central_status != "central"){
    if(messageTemp=="Kiri"){
      digitalWrite(steering1_L, HIGH);
      digitalWrite(steering1_R, LOW);
      //////lcd.setCursor(10,2);
      ////lcd.print("Kiri");
      messageTemp ="";
      
    }
    if(messageTemp=="Kanan"){
      digitalWrite(steering1_L, LOW);
      digitalWrite(steering1_R, HIGH);
      //////lcd.setCursor(10,2);
      ////lcd.print("Kanan");
      messageTemp ="";
      
    } 
    if(messageTemp=="Tahan"){
      digitalWrite(steering1_L, LOW);
      digitalWrite(steering1_R, LOW);
      //////lcd.setCursor(10,2);
      ////lcd.print("Hold ");
      messageTemp ="";
    } 

  }
     messageTemp ="";
 }

if (String(topic) == "Steering_DP 2") {
  if (central_status != "central"){
    if(messageTemp=="Kiri"){
      digitalWrite(steering2_L, HIGH);
      digitalWrite(steering2_R, LOW);
      //////lcd.setCursor(10,2);
      ////lcd.print("Kiri");
      messageTemp ="";
      
    }
    if(messageTemp=="Kanan"){
      digitalWrite(steering2_L, LOW);
      digitalWrite(steering2_R, HIGH);
      //////lcd.setCursor(10,2);
      ////lcd.print("Kanan");
      messageTemp ="";
      
    } 
    if(messageTemp=="Tahan"){
      digitalWrite(steering2_L, LOW);
      digitalWrite(steering2_R, LOW);
      //////lcd.setCursor(10,2);
      ////lcd.print("Hold ");
      messageTemp ="";
    } 

  }
     messageTemp ="";
 }

if (String(topic) == "Steering_DP 3") {
  if (central_status != "central"){
    if(messageTemp=="Kiri"){
      digitalWrite(steering3_L, HIGH);
      digitalWrite(steering3_R, LOW);
      //////lcd.setCursor(10,2);
      ////lcd.print("Kiri");
      messageTemp ="";
      
    }
    if(messageTemp=="Kanan"){
      digitalWrite(steering3_L, LOW);
      digitalWrite(steering3_R, HIGH);
      //////lcd.setCursor(10,2);
      ////lcd.print("Kanan");
      messageTemp ="";
      
    } 
    if(messageTemp=="Tahan"){
      digitalWrite(steering3_L, LOW);
      digitalWrite(steering3_R, LOW);
      //////lcd.setCursor(10,2);
      ////lcd.print("Hold ");
      messageTemp ="";
    } 

  }
     messageTemp ="";
 }




if (String(topic) == "Steering_DP 4") {
  if (central_status != "central"){
       if(messageTemp=="Kiri"){
      digitalWrite(steering4_L, HIGH);
      digitalWrite(steering4_R, LOW);
      ////lcd.setCursor(10,2);
      ////lcd.print("Kiri");
      messageTemp ="";
    }
    if(messageTemp=="Kanan"){
      digitalWrite(steering4_L, LOW);
      digitalWrite(steering4_R, HIGH);
      ////lcd.setCursor(10,2);
      //////lcd.print("Kanan");
      messageTemp ="";
    } 
      if(messageTemp=="Tahan"){
      digitalWrite(steering4_L, LOW);
      digitalWrite(steering4_R, LOW);
      ////lcd.setCursor(10,2);
      //////lcd.print("Hold ");
      messageTemp ="";
      
    } 

  }
   
    
     messageTemp ="";
 }

if (String(topic) == "central_status") {
    central_status = messageTemp;

}


}


void reconnect() { 
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect

    lcd.clear();
    
    
    if (client.connect("SPC1")) {
      Serial.println("connected");

      client.subscribe("propeller1");
      client.subscribe("propeller2");
      client.subscribe("propeller3");
      client.subscribe("propeller4");

      client.subscribe("steering1");
      client.subscribe("steering2");
      client.subscribe("steering3");
      client.subscribe("steering4");

      client.subscribe("Steering_DP 1");
      client.subscribe("Steering_DP 2");
      client.subscribe("Steering_DP 3");
      client.subscribe("Steering_DP 4");

      client.subscribe("central_status");

      client.subscribe("steer1_command");
      client.subscribe("steer2_command");
      client.subscribe("steer3_command");
      client.subscribe("steer4_command");
    
    } else {
      lcd.clear();
      lcd.setCursor(0,0); 
      lcd.print("ATTEMPTING SERVER");
      Serial.print("fail, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");

      // Wait 5 seconds before retrying
      analogWrite (propeller1, 132);
      analogWrite (propeller2, 132);
      delay(2000);
      digitalWrite(reset_pin, HIGH);

    }
        
  } 
 
}




void RPM1() {
  tick1++;
}


void RPM2() {
  tick2++;
}

void RPM3() {
  tick3++;
}


void RPM4() {
  tick4++;
}


void setup(){
  Wire.begin();
  Serial.begin(115200); 
  Serial.println("booting..");
  client.setServer(server, 1883);
  client.setCallback(callback);

  
  Ethernet.begin(mac, ip);
  
  pinMode(button_L, INPUT_PULLUP);
  pinMode(button_R, INPUT_PULLUP);

  pinMode(button_mode_local, INPUT_PULLUP);

  pinMode(propeller_select1, INPUT_PULLUP);
  pinMode(propeller_select2, INPUT_PULLUP);

  pinMode(reset_pin, OUTPUT);
  digitalWrite(reset_pin, LOW);

  pinMode(steering1_L, OUTPUT);
  pinMode(steering1_R, OUTPUT);

  pinMode(steering2_L, OUTPUT);
  pinMode(steering2_R, OUTPUT);

  pinMode(steering3_L, OUTPUT);
  pinMode(steering3_R, OUTPUT);

  pinMode(steering4_L, OUTPUT);
  pinMode(steering4_R, OUTPUT);
  
  pinMode(propeller1, OUTPUT);
  pinMode(propeller2, OUTPUT);


  analogWrite (propeller1, 132);
  analogWrite (propeller2, 132);

  digitalWrite(steering1_L, LOW);
  digitalWrite(steering1_R, LOW);

  digitalWrite(steering2_L, LOW);
  digitalWrite(steering2_R, LOW);

  digitalWrite(steering3_L, LOW);
  digitalWrite(steering3_R, LOW);

  digitalWrite(steering4_L, LOW);
  digitalWrite(steering4_R, LOW);


  attachInterrupt(0, RPM1, FALLING);
  attachInterrupt(1, RPM2, FALLING);


  lcd.init(); 
  
  
  delay(500);



  for(int i = 0; i< 3; i++)
  {
    lcd.backlight();
    delay(250);
    lcd.noBacklight();
    delay(250);
  }
  lcd.backlight();  

 
  //lcd.setCursor(1,0); 
  //lcd.print("Syergie Indo Prima");
  //lcd.setCursor(0,1);
  //lcd.print("--------------------");
  delay(1000);  
  //lcd.setCursor(8,2);
  //lcd.print("SPC 1");
  //lcd.setCursor(0,3);
  //lcd.print("--------------------");
  delay(1000);
  lcd.clear();
   
 
  TCCR0B = (TCCR0B & 0b11111000) | 0x05;  // 60 hz
  
  wdt_enable(WDTO_4S);
}


static char RPM_OUT1[10];
static char steering1_send[10];
static char steering2_send[10];
static char rpm_send[10];
static char rpm2_send[10];
static char delta_orifice_send[10];
static char pressure1_send[10];
static char pressure2_send[10];


static char delta_orifice2_send[10];
static char pressure3_send[10];
static char pressure4_send[10];
static char flow_lpm_send[10];
static char flow_lpm2_send[10];
static char time_loop_send[10];

void loop(){
  
  Time = millis();

  time_loop = millis() - time_loop_prev;

  steering1 = map(analogRead(A12),0, 1023,0,360);
  steering2 = map(analogRead(A13),0, 1023,0,360);
  steering3 = map(analogRead(A14),0, 1023,0,360);
  steering4 = map(analogRead(A15),0, 1023,0,360);
  
  buttonstate_L = digitalRead(button_L);
  buttonstate_R = digitalRead(button_R);


  
//-----------------------------------------------------------------

  mode_state = !digitalRead(button_mode_local);
  if(mode_state!=mode_state_prev){
    //lcd.clear();
  }
//mode Local
   if(mode_state ==  LOW){

    wdt_reset();

    char buffer[21];
    sprintf(buffer, "str:%d gas:%d", steering1, pwm1_buffer);
    //lcd.setCursor(0, 1);
    //lcd.print(buffer);
 
  speed_motor = map(analogRead(SLIDER), 0, 1023, 0, 100);

  if (!digitalRead(propeller_select1) == LOW){

  
  analogWrite (propeller1, map(speed_motor, 0, 100, 132, 255)); 
  /*
  //lcd.setCursor(10,3);
  //lcd.print("Local1");
  
  if (buttonstate_L == LOW){
      //lcd.setCursor( 10,2);
      //lcd.print("Kiri 1");
      digitalWrite(steering1_L, HIGH);
      digitalWrite(steering1_R, LOW);
  }

  if(buttonstate_R == LOW){
      //lcd.setCursor(10,2);
      //lcd.print("Kanan1");
      digitalWrite(steering1_L, LOW);
      digitalWrite(steering1_R, HIGH);
  }
  */
    
  }


  if (!digitalRead(propeller_select2) == LOW){

  analogWrite (propeller2, map(speed_motor, 0, 100, 132, 255));

  //lcd.setCursor(10,3);
  //lcd.print("Local4");
  if (buttonstate_L == LOW){
      //lcd.setCursor( 10,2);
      //lcd.print("Kiri 4");
      digitalWrite(steering4_L, HIGH);
      digitalWrite(steering4_R, LOW);
      
  }

  if(buttonstate_R == LOW){
      //lcd.setCursor(10,2);
      //lcd.print("Kanan4");
      digitalWrite(steering4_L, LOW);
      digitalWrite(steering4_R, HIGH);
  }
    
  }
  
 

  if(buttonstate_L == buttonstate_R){
    //lcd.setCursor(10,2);
    //lcd.print("Hold  ");
    digitalWrite(steering1_L, LOW);
    digitalWrite(steering1_R, LOW);
    digitalWrite(steering4_L, LOW);
    digitalWrite(steering4_R, LOW);
  }

    wdt_reset();
    
  }


//--------------------------------------------------------------------  
  // Mode Central

  else if(mode_state ==  HIGH){

  if (!client.connected()) {
    reconnect();
    
  } else {
    wdt_reset();
  }
  
  
  client.loop();


  if (central_status == "central"){
      steer1_error = shortest_psi(steering1, steer1_command);

      if(abs(steer1_error) < 3){
        digitalWrite(steering1_L, LOW);
        digitalWrite(steering1_R, LOW);
      } else {
        if (steer1_error > 0){
        digitalWrite(steering1_L, LOW);
        digitalWrite(steering1_R, HIGH);
        } else {
        digitalWrite(steering1_L, HIGH);
        digitalWrite(steering1_R, LOW);

        }
      }

      steer2_error = shortest_psi(steering2, steer2_command);

      if(abs(steer2_error) < 3){
        digitalWrite(steering2_L, LOW);
        digitalWrite(steering2_R, LOW);
      } else {
        if (steer2_error > 0){
        digitalWrite(steering2_L, LOW);
        digitalWrite(steering2_R, HIGH);
        } else {
        digitalWrite(steering2_L, HIGH);
        digitalWrite(steering2_R, LOW);

        }
      }

    steer3_error = shortest_psi(steering3, steer3_command);

      if(abs(steer3_error) < 3){
        digitalWrite(steering3_L, LOW);
        digitalWrite(steering3_R, LOW);
      } else {
        if (steer3_error > 0){
        digitalWrite(steering3_L, LOW);
        digitalWrite(steering3_R, HIGH);
        } else {
        digitalWrite(steering3_L, HIGH);
        digitalWrite(steering3_R, LOW);

        }
      }

    steer4_error = shortest_psi(steering4, steer4_command);

      if(abs(steer4_error) < 3){
        digitalWrite(steering4_L, LOW);
        digitalWrite(steering4_R, LOW);
      } else {
        if (steer4_error > 0){
        digitalWrite(steering4_L, LOW);
        digitalWrite(steering4_R, HIGH);
        } else {
        digitalWrite(steering4_L, HIGH);
        digitalWrite(steering4_R, LOW);

        }
      }

    
  }
  

    pwm1 = pwm1_buffer;
    pwm2 = pwm2_buffer;


  message_time = millis() - prev_message_time;
  if (message_time > 62){
    /*
    //lcd.setCursor(8,0); 
    //lcd.print("SPC 1");
    //lcd.setCursor (0,1);
    //lcd.print("Speed   :");
   
    //lcd.setCursor(0,2);
    //lcd.print("Azimuth :");
    //lcd.setCursor(0,3);
    //lcd.print("Mode    :");

    ////lcd.setCursor(10,3);
    //lcd.print("Central");
    //lcd.print("  ");
    */
    char P1[21];
    sprintf(P1, " P1 str:%-4d gas:%-4d", steering1, pwm1_buffer);
    lcd.setCursor(0, 0);
    lcd.print(P1);


    char P2[21];
    sprintf(P2, " P2 str:%-4d gas:%-4d", steering2, pwm2_buffer);
    lcd.setCursor(0, 0);
    lcd.print(P2);



    char P3[21];
    sprintf(P3, " P3 str:%-4d gas:%-4d", steering3, 0);
    lcd.setCursor(0, 0);
    lcd.print(P1);



    char P4[21];
    sprintf(P4, " P4 str:%-4d gas:%-4d", steering4, 0);
    lcd.setCursor(0, 0);
    lcd.print(P1);

    
    
    if (!digitalRead(propeller_select2) == HIGH){

    ////lcd.print("MOTOR1");
    }
    
    if (!digitalRead(propeller_select2) == LOW){

    ////lcd.print("MOTOR4");
    }
    
  
  
  client.publish("SPC1", "Central");
  client.publish("steering1_sensor", dtostrf(steering1,6,0,steering1_send));
  client.publish("steering2_sensor", dtostrf(steering2,6,0,steering2_send));
  client.publish("steering3_sensor", dtostrf(steering3,6,0,steering2_send));
  client.publish("steering4_sensor", dtostrf(steering4,6,0,steering2_send));

  client.publish("rpm1", dtostrf(rpm_filtered,6,0,rpm_send));
  client.publish("rpm2", dtostrf(rpm2_filtered,6,0,rpm2_send));

  client.publish("dt", dtostrf(time_loop,6,0,time_loop_send));

  prev_message_time = millis();
  
  }

  analogWrite(propeller1,pwm1);
  analogWrite(propeller2,pwm2);

  
elapsed_time = Time - prev_time;
rpm_time = millis() - prev_rpm_time;

if(rpm_time > 62){

  ////lcd.setCursor(8,0); 
  //lcd.print("SPC 1");
  ////lcd.setCursor (0,1);
  //lcd.print("Speed   :");
   
  ////lcd.setCursor(0,2);
  //lcd.print("Azimuth :");
  ////lcd.setCursor(0,3);
  //lcd.print("Mode    :");

  
  rpm = tick1 * 60;
  rpm_filtered = (0.3 * rpm_filtered) + (0.7 * float(rpm));
  tick1 = 0;

  rpm2 = tick2 * 60;
  rpm2_filtered = (0.3 * rpm2_filtered) + (0.7 * float(rpm2));
  tick2 = 0;

  Serial.print(pwm1);
  Serial.print("  ");
  Serial.println(pwm2);
  prev_rpm_time = millis();
  
}


prev_time = Time;
time_loop_prev = millis();

}



}
