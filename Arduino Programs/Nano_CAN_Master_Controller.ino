#include <SPI.h>
#include <mcp2515.h>

struct can_frame canControl;  // TX: Request status ping
struct can_frame canMsg;      // RX: Any incoming CAN messages
struct can_frame canGo;       // TX: "Go" signal to tell sensors to collect data
MCP2515 mcp(10);              // Identify where the "CS" (aka "SS") pin is connected

String incomingSerial;           // Variable for holding incoming serial data

unsigned int starttime;
unsigned int time;            // Variables to track time
byte pingCount = 0;           // Count number of devices on CAN bus


void setup() {
  // Pre-defining messsages that can be sent on the CAN bus
  canControl.can_id = 0x7E;                   // Set master controller's ID ("~" in hex)
  canControl.can_dlc = 2;                     // Sending 2 bytes of data
  canControl.data[0] = byte("r");
  canControl.data[1] = byte("?");             // Define message

  canGo.can_id = 0x7E;                        // Using the same master controller ID
  canGo.can_dlc = 1;                          // Just one byte of data
  canGo.data[0] = byte("G");                  // "Go" signal


  Serial.begin(1000000);  // Use fastest baud rate that the Pi can support for max data thruput
  Serial.println(F("Serial connection to PC initialized"));
  
  mcp.reset();
  mcp.setBitrate(CAN_500KBPS, MCP_8MHZ); // Set up the CAN module
  mcp.setNormalMode();                    // Will not read its own messages
  delay(100);                             // Mandatory delay
  Serial.println(F("CAN Connection initialized"));


  // After startup, send a "ping" signal to figure out which other Arduinos are on the network
  Serial.println(F("Giving Arduinos time to boot up..."));
  delay(5500);                           // First wait for all Arduinos to complete startup tests
  mcp.sendMessage(&canControl);           // Then send message
  delay(10);
  Serial.println(F("Pinging CAN network..."));
  starttime = millis();
  while (time <= 2000 + starttime){
    if (mcp.readMessage(&canMsg) == MCP2515::ERROR_OK) {
      Serial.print(F("Response: "));
      Serial.write(canMsg.can_id); 
      Serial.write(0x20);
      if (canMsg.can_id == 0x5E){
        Serial.write(canMsg.data[0]); 
        Serial.write(0x20);
      }
      Serial.println();
      pingCount ++;
    }
    time = millis();
  }
  Serial.print(F("Responses from "));
  Serial.print(pingCount);
  Serial.println(F(" of 3 Arduinos"));
  delay(100);

  Serial.println(F("Nano Pass-Through ready"));   // Announce startup complete
  pinMode(13, OUTPUT);
  digitalWrite(13, HIGH);                         // Turn on built-in LED
  delay(100);

  //mcp.sendMessage(&canGo);                      // "Get data" request for debugging
}

void loop() {
  if (mcp.readMessage(&canMsg) == MCP2515::ERROR_OK) {
    if (canMsg.can_id != 0x5E){
      Serial.write(canMsg.can_id);     // Print ID as hex (for Python interpreter)
    } 
    //Serial.print(char(canMsg.can_id));  // Print ID as character
    //Serial.print(" ");
    //Serial.print(canMsg.can_dlc, HEX);  // print message length
    //Serial.print(" ");
    
    if (canMsg.can_id == 0x5E){                // Listen for data termination message
      //Serial.print(char(canMsg.data[0]));
      //Serial.print(" ");
      //Serial.write(canMsg.data[0]);       // Print  as hex (for Python interpreter)
      for(byte i = 0; i < 5; i ++){
        Serial.write(0x7E);                 // Print a unique set of characters that data can never recreate
      }
    }
    else{
      for (int i = 0; i<canMsg.can_dlc; i++)  {  // Print the data for anything
        //Serial.print(canMsg.data[i], BIN);       // in binary for human
        //Serial.print(" ");
        Serial.write(canMsg.data[i]);       // (For Python interpreter)
      }
    }

    //Serial.println();      // New line after entire CAN message has been recieved and passed through
  }


  while(Serial.available() != 0){               // If there is an incoming serial message from Python controller...
    delay(10);
    String incomingSerial = Serial.readStringUntil('\n');     // Store it as a variable...

    if (incomingSerial == -1){              // Check if there is actually any data...
      Serial.println("error");
      goto srxErrOut;                       // If for some reason there isn't anything there, just move on
    }
    else if (incomingSerial == "G"){        // If it recieves the "Go" signal...
      mcp.sendMessage(&canGo);              // Rebroadcast over CAN bus
    }      
    else{                                   // Otherwise...
      Serial.write(0x3F);                   // Tell the Python controller the commmand was unrecognized
      Serial.write(0x0A);
    }
  }
  srxErrOut:                              // Serial RX Error Out "safe resume" point
  delay(0);
}
