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
#define motor (12)
#define motor4 (11)


#define angular_pin1 (A1)
#define angular_pin2 (A2)

int Propeller1 = 0;
int PropellerM = 0;
int lcd_speedM ;
int lcd_speed2M ;

int pwm  = 132;
int pwm2 = 132;
int Angular1 = 0;
int Angular4 = 0;
int degree1 = 0;
int degree2 = 0;
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

int tick;
int tick2;
float rpm_filtered;


int orifice1A;
#define orifice1A_analog (A2)
int orifice1B;
#define orifice1B_analog (A3)

int orifice2A;
#define orifice2A_analog (A4)
int orifice2B;
#define orifice2B_analog (A5)

int delta_orifice;

int delta_orifice2;


#define button_L (31)
#define button_R (33)
#define button_mode_central (23)
#define button_mode_local (25)

int buttonstate_L = 0;
int buttonstate_R = 0;
int buttonstate_M = 0;

#define SSR_L (9)
#define SSR_R (8)

#define SSR_L_4 (6)
#define SSR_R_4 (5)

int propeller_select1 = 27;
int propeller_select2 = 29;


EthernetClient ethClient;
PubSubClient client(ethClient);


// Update these with values suitable for your network.
byte mac[]    = {  0xDE, 0xED, 0xBA, 0xFE, 0xFE, 0xE1 };
IPAddress ip(123, 45, 0, 102);
IPAddress server(123, 45, 0, 10);

int mode_state;
int mode_state_prev;

void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  String messageTemp;
  
  for (int i=0;i<length;i++) {

    //Serial.print((char)payload[i]);
   messageTemp += (char)message[i];
  }
  

  
  //Serial.println();
if (String(topic) == "Set_Speed2M") {
     pwm = messageTemp.toInt(); 
     lcd_speedM = map(pwm, 132,255,0,100); 
     
     messageTemp ="";
   }


if (String(topic) == "Set_Speed3M") {
     pwm2 = messageTemp.toInt(); 
     lcd_speed2M = map(pwm2, 132,255,0,100); 
     
     messageTemp ="";
   }

   
if (String(topic) == "Steering_DP 2") {
  
    if(messageTemp=="Kiri"){
      digitalWrite(SSR_L, HIGH);
      digitalWrite(SSR_R, LOW);
      lcd.setCursor(10,2);
      lcd.print("Kiri");
      messageTemp ="";
      
    }
    if(messageTemp=="Kanan"){
      digitalWrite(SSR_L, LOW);
      digitalWrite(SSR_R, HIGH);
      lcd.setCursor(10,2);
      lcd.print("Kanan");
      messageTemp ="";
      
    } 
    if(messageTemp=="Tahan"){
      digitalWrite(SSR_L, LOW);
      digitalWrite(SSR_R, LOW);
      lcd.setCursor(10,2);
      lcd.print("Hold ");
      messageTemp ="";
      
    } 
    
     messageTemp ="";
 }


if (String(topic) == "Steering_DP 3") {
  
    if(messageTemp=="Kiri"){
      digitalWrite(SSR_L_4, HIGH);
      digitalWrite(SSR_R_4, LOW);
      lcd.setCursor(10,2);
      lcd.print("Kiri");
      messageTemp ="";
    }
    if(messageTemp=="Kanan"){
      digitalWrite(SSR_L_4, LOW);
      digitalWrite(SSR_R_4, HIGH);
      lcd.setCursor(10,2);
      lcd.print("Kanan");
      messageTemp ="";
    } 
      if(messageTemp=="Tahan"){
      digitalWrite(SSR_L_4, LOW);
      digitalWrite(SSR_R_4, LOW);
      lcd.setCursor(10,2);
      lcd.print("Hold ");
      messageTemp ="";
      
    } 
    
     messageTemp ="";
 }




}


void reconnect() { 
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("SPC2")) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      //client.publish("outTopic","hello world");
      // ... and resubscribe

   
      client.subscribe("Set_Speed2M");
      client.subscribe("Steering_DP 2");

      client.subscribe("Set_Speed3M");
      client.subscribe("Steering_DP 3");
    
    } else {
      lcd.clear();
      lcd.setCursor(0,0); 
      lcd.print("ATTEMPTING SERVER");
      Serial.print("fail, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");

      // Wait 5 seconds before retrying
      analogWrite (motor, 132);
      delay(2000);
      digitalWrite(reset_pin, HIGH);

    }
        
  } 
 
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
  pinMode(button_mode_central, INPUT_PULLUP);
  pinMode(button_mode_local, INPUT_PULLUP);

  pinMode(propeller_select1, INPUT_PULLUP);
  pinMode(propeller_select2, INPUT_PULLUP);

  pinMode(SSR_L, OUTPUT);
  pinMode(SSR_R, OUTPUT);
  pinMode(motor, OUTPUT);
  
  pinMode(reset_pin, OUTPUT);
  digitalWrite(reset_pin, LOW);

  pinMode(SSR_L_4, OUTPUT);
  pinMode(SSR_R_4, OUTPUT);
  pinMode(motor4, OUTPUT);


  analogWrite (motor, 132);
  analogWrite (motor4, 132);

  attachInterrupt(0, RPM1, FALLING);
  attachInterrupt(1, RPM2, FALLING);


  //kalo error pake salah satunya
  //lcd.begin();
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

 
  lcd.setCursor(1,0); 
  lcd.print("Syergie Indo Prima");
  lcd.setCursor(0,1);
  lcd.print("--------------------");
  delay(1000);  
  lcd.setCursor(8,2);
  lcd.print("SPC 2");
  lcd.setCursor(0,3);
  lcd.print("--------------------");
  delay(1000);
  lcd.clear();
   
 
  TCCR0B = (TCCR0B & 0b11111000) | 0x05;  // 60 hz


  
  wdt_enable(WDTO_4S);
}


static char RPM_OUT1[10];
static char degree1_send[10];
static char degree2_send[10];
static char rpm_send[10];
static char rpm2_send[10];
static char delta_orifice_send[10];
static char pressure1_send[10];
static char pressure2_send[10];


static char delta_orifice2_send[10];
static char pressure3_send[10];
static char pressure4_send[10];

void loop(){
  
  Time = millis();
        
  Angular1 = analogRead(angular_pin1);
  Angular4 = analogRead(angular_pin2);
  degree1 = map(Angular1,0,1023,0,360);
  degree2 = map(Angular1,0, 1023,0,360);
  
  buttonstate_L = digitalRead(button_L);
  buttonstate_R = digitalRead(button_R);


  //read orifice
  orifice1A = analogRead(orifice1A_analog);
  orifice1B = analogRead(orifice1B_analog);

  orifice2A = analogRead(orifice2A_analog);
  orifice2B = analogRead(orifice2B_analog);

  
  delta_orifice = (0.1 * abs(orifice1A - orifice1B)) + (0.9 * delta_orifice);

  delta_orifice2 = (0.1 * abs(orifice2A - orifice2B)) + (0.9 * delta_orifice2);
  
  lcd.setCursor(8,0); 
  lcd.print("SPC 1");
  lcd.setCursor (0,1);
  lcd.print("Speed   :");
 
  lcd.setCursor(0,2);
  lcd.print("Azimuth :");
  lcd.setCursor(0,3);
  lcd.print("Mode    :");

 
//-----------------------------------------------------------------
mode_state = !digitalRead(button_mode_local);
  if(mode_state!=mode_state_prev){
    lcd.clear();
  }



//mode Local
   if(mode_state ==  LOW){

    lcd.setCursor(8,0); 
    lcd.print("SPC 2");
    lcd.setCursor (0,1);
    lcd.print("Speed   :");
   
    lcd.setCursor(0,2);
    lcd.print("Azimuth :");
    lcd.setCursor(0,3);
    lcd.print("Mode    :");
    lcd.print("  ");
    lcd.setCursor(10,1);
    lcd.print(speed_motor);
    lcd.print("  ");
 
    
  if (!digitalRead(propeller_select1) == LOW){

  speed_motor = map(analogRead(SLIDER), 0, 1023, 0, 100);
  analogWrite (motor, map(speed_motor, 0, 100, 132, 255)); //220 UNTUK 11 V. 255 untuk 12V
  lcd.setCursor(10,3);
  lcd.print("Local2");
  
  if (buttonstate_L == LOW){
      lcd.setCursor( 10,2);
      lcd.print("Kiri2");
      digitalWrite(SSR_L, HIGH);
      digitalWrite(SSR_R, LOW);
  }

  if(buttonstate_R == LOW){
      lcd.setCursor(10,2);
      lcd.print("Kanan2");
      digitalWrite(SSR_L, LOW);
      digitalWrite(SSR_R, HIGH);
  }
    
  }


  if (!digitalRead(propeller_select1) == HIGH){

  speed_motor = map(analogRead(SLIDER), 0, 1023, 0, 100);
  analogWrite (motor4, map(speed_motor, 0, 100, 132, 255)); //220 UNTUK 11 V. 255 untuk 12V

  
  if (buttonstate_L == LOW){
      lcd.setCursor( 10,2);
      lcd.print("Kiri3");
      digitalWrite(SSR_L_4, HIGH);
      digitalWrite(SSR_R_4, LOW);
  }

  if(buttonstate_R == LOW){
      lcd.setCursor(10,2);
      lcd.print("Kanan3");
      digitalWrite(SSR_L_4, LOW);
      digitalWrite(SSR_R_4, HIGH);
  }
    
  }
  
 

  if(buttonstate_L == buttonstate_R){
    lcd.setCursor(10,2);
    lcd.print("Hold ");
    digitalWrite(SSR_L, LOW);
    digitalWrite(SSR_R, LOW);
    digitalWrite(SSR_L_4, LOW);
    digitalWrite(SSR_R_4, LOW);
  }

  
    
  }


//--------------------------------------------------------------------  
// Mode Central

  else if(!digitalRead(button_mode_central) ==  LOW){

  if (!client.connected()) {
    reconnect();
    
  } else {
    wdt_reset();
  }
  
  
  client.loop();
  
  

      


  message_time = millis() - prev_message_time;
  if (message_time > 62){

    lcd.setCursor(8,0); 
    lcd.print("SPC 2");
    lcd.setCursor (0,1);
    lcd.print("Speed   :");
   
    lcd.setCursor(0,2);
    lcd.print("Azimuth :");
    lcd.setCursor(0,3);
    lcd.print("Mode    :");

    lcd.setCursor(10,3);
    lcd.print("Central");
    lcd.print("  ");

    if (!digitalRead(propeller_select2) == HIGH){
    lcd.setCursor(10,1);
    lcd.print(lcd_speedM);
    lcd.print("   ");
    lcd.setCursor(14,1);
    lcd.print("MOTOR2");
    }
    
    if (!digitalRead(propeller_select2) == LOW){
    lcd.setCursor(10,1);
    lcd.print(lcd_speed2M);
    lcd.print("   ");
    lcd.setCursor(14,1);
    lcd.print("MOTOR3");
    }
    
  
  client.publish("SPC2", "Central");
  client.publish("steering2", dtostrf(degree1,6,0,degree1_send));
  client.publish("steering3", dtostrf(degree2,6,0,degree2_send));
  client.publish("mesin2", dtostrf(rpm_filtered,6,0,rpm_send));
  client.publish("flow2", dtostrf(delta_orifice,6,0,delta_orifice_send));
  client.publish("rpm2", dtostrf(rpm_filtered,6,0,rpm_send));
  client.publish("rpm3", dtostrf(rpm2_filtered,6,0,rpm2_send));

  prev_message_time = millis();
  Serial.println("loop");
  }

  analogWrite(motor,pwm);
  analogWrite(motor4,pwm2);
  
  

  }
  
elapsed_time = Time - prev_time;
rpm_time = millis() - prev_rpm_time;

if(rpm_time > 62){
  rpm = tick * 60;
  rpm_filtered = (0.3 * rpm_filtered) + (0.7 * float(rpm));
  tick = 0;

  rpm2 = tick2 * 60;
  rpm2_filtered = (0.3 * rpm2_filtered) + (0.7 * float(rpm2));
  tick2 = 0;

  
  prev_rpm_time = millis();
}


prev_time = Time;


}


void RPM1() {
  tick++;
}


void RPM2() {
  tick2++;
}
