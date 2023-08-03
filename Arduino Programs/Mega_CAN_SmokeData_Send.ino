#include <SPI.h>
#include <mcp2515.h>
#include <CD74HC4067.h>

struct can_frame canData;   // Structure for sending data
struct can_frame canStatus; // Structure for signaling end of data
struct can_frame canMsg;    // Structure for incomming messages
MCP2515 mcp(53);            // Defining CS pin for SPI communications

CD74HC4067 muxA1(36, 37, 38, 39);  // Telling the library where to find the multiplexer control pins
CD74HC4067 muxA2(40, 41, 42, 43);
CD74HC4067 muxA3(44, 45, 46, 47);
CD74HC4067 muxB1(22, 23, 24, 25);
CD74HC4067 muxB2(26, 27, 28, 29);
CD74HC4067 muxB3(30, 31, 32, 33);

long smkN;                  // Variable to hold each sensor's data as they are read
long smks[96];              // No more than 96 sensors can physically be connected to the mux array



void setup() {
  canData.can_id  = 0x53;  // This ID tag is hex for "S"
  canData.can_dlc = 1;
  canData.data[0];

  canStatus.can_id = 0x5E;   // Character "^" to define a status message
  canStatus.can_dlc = 1;
  canStatus.data[0] = canData.can_id;

  Serial.begin(1000000);
  
  mcp.reset();
  mcp.setBitrate(CAN_1000KBPS, MCP_8MHZ);
  mcp.setNormalMode();
  delay(100);

  pinMode(A0, INPUT);    // Analog Pins for sensor reading
  pinMode(A1, INPUT);
  pinMode(A2, INPUT);
  pinMode(A3, INPUT);
  pinMode(A4, INPUT);
  pinMode(A5, INPUT);

  for(int i = 22; i <= 47; i++){
    pinMode(i, OUTPUT);           // Using a loop to define all 24 digital pins as outputs
  }
}

void loop() {
  if (mcp.readMessage(&canMsg) == MCP2515::ERROR_OK) {
    if (canMsg.can_id == 0x7E && canMsg.can_dlc == 2){   // Listen for a message from master control unit
      mcp.sendMessage(&canStatus);                       // send back status
      Serial.println("ACK sent to master's ping (S)");
    }
  }
  
  for(int i = 0; i <= 15; i ++){
    muxA1.channel(i);                                                   // Set channel # (0 -> 15)
    smkN = constrain(analogRead(A0), 250, 1000);                     // Take reading from common analog pin
    smks[i] = constrain(map(smkN, 250, 1000, 0, 15000), 0, 15000);   // Convert readings to approximate PPMs
  }
  for(int i = 0; i <= 15; i ++){
    muxA2.channel(i);
    smkN = constrain(analogRead(A1), 250, 1000);                     // Take reading from common analog pin
    smks[i + 15] = constrain(map(smkN, 250, 1000, 0, 15000), 0, 15000);   // Convert readings to approximate PPMs
  }
  for(int i = 0; i <= 15; i ++){
    muxA3.channel(i);
    smkN = constrain(analogRead(A2), 250, 1000);                     // Take reading from common analog pin
    smks[i + 15 + 15] = constrain(map(smkN, 250, 1000, 0, 15000), 0, 15000);   // Convert readings to approximate PPMs
  }
  for(int i = 0; i <= 15; i ++){
    muxB1.channel(i);
    smkN = constrain(analogRead(A3), 250, 1000);                     // Take reading from common analog pin
    smks[i + 15 + 15 + 15] = constrain(map(smkN, 250, 1000, 0, 15000), 0, 15000);   // Convert readings to approximate PPMs
  }
  for(int i = 0; i <= 15; i ++){
    muxB2.channel(i);
    smkN = constrain(analogRead(A4), 250, 1000);                     // Take reading from common analog pin
    smks[i + 15 + 15 + 15 + 15] = constrain(map(smkN, 250, 1000, 0, 15000), 0, 15000);   // Convert readings to approximate PPMs
  }
  for(int i = 0; i <= 15; i ++){
    muxB3.channel(i);
    smkN = constrain(analogRead(A5), 250, 1000);                     // Take reading from common analog pin
    smks[i + 15 + 15 + 15 + 15 + 15] = constrain(map(smkN, 250, 1000, 0, 15000), 0, 15000);   // Convert readings to approximate PPMs
  }
  
  for(int i = 0; i < 96; i++){
    Serial.print(smks[i]);
    Serial.print(" ");
  }
  Serial.println();

  delay(1000);

}
