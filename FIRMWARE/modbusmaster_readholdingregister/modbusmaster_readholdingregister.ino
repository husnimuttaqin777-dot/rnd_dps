#include<ModbusMaster.h>


#define MAX485_DE 3
#define MAX485_RE_NEG 2

//DI => TX
//RO => RX


ModbusMaster node;

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
  Serial1.begin(4800);

  pinMode(MAX485_RE_NEG, OUTPUT);
  pinMode(MAX485_DE, OUTPUT);

  // Init in receive mode
  digitalWrite(MAX485_RE_NEG, 1);
  digitalWrite(MAX485_DE, 1);

  //My slave uses 9600 baud

  Serial.begin(9600);
  delay(10);
  Serial.println("starting arduino: ");
  Serial.println("setting up Serial ");
  Serial.println("setting up RS485 port ");
//  slave id
  node.begin(1, Serial1);
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);
}


void loop() {
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
      
      Serial.print("Register ");
      Serial.print(i);
      Serial.print(": ");
      Serial.println(data[i]);

      }
    }
  } else {
    Serial.println("Failed to read holding registers!");
  }

}
