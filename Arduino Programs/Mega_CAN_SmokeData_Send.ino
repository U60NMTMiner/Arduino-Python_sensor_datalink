#include <SPI.h>
#include <mcp2515.h>
#include <CD74HC4067.h>

struct can_frame canData;   // Structure for sending data
struct can_frame canStatus; // Structure for signaling end of data
struct can_frame canMsg;    // Structure for incomming messages
MCP2515 mcp(53);            // Defining CS pin for SPI communications
bool go = false;

CD74HC4067 muxA1(36, 37, 38, 39);  // Telling the library where to find the multiplexer control pins
CD74HC4067 muxA2(40, 41, 42, 43);
CD74HC4067 muxA3(44, 45, 46, 47);
CD74HC4067 muxB1(22, 23, 24, 25);
CD74HC4067 muxB2(26, 27, 28, 29);
CD74HC4067 muxB3(30, 31, 32, 33);

long smkN;                  // Variable to hold each sensor's data as they are read
long smks[96];              // No more than 96 sensors can physically be connected to the mux array


// Function to convert an long integer into 4 bytes
byte databytes[4];
void I2B(long value, byte* bytes) {
  // Break the integer into 4 bytes
  bytes[0] = (value >> 24) & 0xFF;
  bytes[1] = (value >> 16) & 0xFF;
  bytes[2] = (value >> 8) & 0xFF;
  bytes[3] = value & 0xFF;
}
// Function to convert back from 4 bytes into a long integer
long B2I(byte* bytes) {
  // Combine the 4 bytes into a long integer
  long value = 0;
  value = ((long)bytes[0] << 24) | ((long)bytes[1] << 16) | ((long)bytes[2] << 8) | (long)bytes[3];
  return value;
}


void setup() {
  canData.can_id  = 0x53;  // This ID tag is hex for "S"
  canData.can_dlc = 4;
  canData.data[3];

  canStatus.can_id = 0x5E;   // Character "^" to define a status message
  canStatus.can_dlc = 1;
  canStatus.data[0] = canData.can_id;

  Serial.begin(1000000);
  Serial.println(F("Serial connection to PC initialized"));
  
  mcp.reset();
  mcp.setBitrate(CAN_1000KBPS, MCP_8MHZ);
  mcp.setNormalMode();
  delay(100);
  Serial.println(F("CAN Connection initialized"));

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
    if (canMsg.can_id == 0x7E && canMsg.can_dlc == 2){   // Listen for startup ping from master control unit
      mcp.sendMessage(&canStatus);                       // send back status
      delay(10);
      Serial.println("ACK sent to master's ping (S)");
      Serial.println();
    }
    else if (canMsg.can_id == 0x7E && canMsg.can_dlc == 1){  // Listen for "Go" message from master control
      go = true;
      // Collect data from all sensors
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
    }
    
    // Wait for the airspeed's end of data before broadcasting
    else if (canMsg.can_id == 0x5E && canMsg.data[0] == 0x41 && go == true){  // go=True condition to prevent spamming after Master's ping
      delay(5);
      for(int i = 0; i < 93; i++){                // For all 93 smoke sensors...
        I2B(long(smks[i]), databytes);            // Convert data from ints to bytes...
        for(int o = 0; o < 4; o++){               // (Need 4 bytes to hold all data)
          canData.data[o] = databytes[o];         // Put data (as 4 bytes) into the CAN message...
        }
        mcp.sendMessage(&canData);                // And send the message
        delay(7);                                 // Mandatory delay (minimum 4 ms)
        Serial.print(smks[i], BIN);
        Serial.print(" ");
      }
      Serial.println();
      mcp.sendMessage(&canStatus);              // Then send terminator to signal end of data
      delay(10);
      Serial.println("Data sent over CAN");
      Serial.println();
      go = false;
    }
  }
}
