#include <SPI.h>
#include <mcp2515.h>

struct can_frame canControl;  // TX: Request status ping
struct can_frame canMsg;      // RX: Any incoming CAN messages
struct can_frame canGo;       // TX: "Go" signal to tell sensors to collect data
MCP2515 mcp(10);          // Identify where the "CS" (aka "SS") pin is connected

int incomimgByte;             // Variable for holding incoming serial data


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
  mcp.reset();
  mcp.setBitrate(CAN_1000KBPS, MCP_8MHZ); // Set up the CAN module
  mcp.setNormalMode();                    // Will not read its own messages
  delay(100);                             // Mandatory delay
  
  // After startup, send a "ping" signal to figure out which other Arduinos are on the network
  mcp.sendMessage(&canControl);           // Send message
  delay(10);

  Serial.println(F("Nano Pass-Through ready"));   // Announce startup complete
}

void loop() {
  if (mcp.readMessage(&canMsg) == MCP2515::ERROR_OK) {
    Serial.write(canMsg.can_id);     // Print ID as hex (for Python interpreter)
    Serial.write(0x20);                 // "space" character instead of spacebar
    //Serial.print(char(canMsg.can_id));  // Print ID as character
    //Serial.print(" ");
    //Serial.print(canMsg.can_dlc, HEX);  // print message length
    //Serial.print(" ");
    
    if (canMsg.can_id == 0x5E){                // Listen for data termination message
      //Serial.print(char(canMsg.data[0]));
      //Serial.print(" ");
      Serial.write(canMsg.data[0]);       // Print as hex (for Python interpreter)
      Serial.write(0x20);
    }
    else{
      for (int i = 0; i<canMsg.can_dlc; i++)  {  // Print the data for anything
        //Serial.print(canMsg.data[i], BIN);       // in binary for human
        //Serial.print(" ");
        Serial.write(canMsg.data[i]);       // (For Python interpreter)
        Serial.write(0x20);
      }
    }

    Serial.println();      // New line after entire CAN message has been recieved and passed through
  }


  if(Serial.available() > 0){             // If there is an incoming serial message from Python controller...
    incomimgByte = Serial.read();         // Store it as a variable...

    if (incomingByte == -1){              // Check if there is actually any data...
      goto srxErrOut;                        // If for some reason there isn't anything there, just move on
    }
    else if (char(incomingByte) == "G"){  // If it recieves the "Go" signal...
      mcp.sendMessage(&canGo);            // Rebroadcast over CAN bus
    }
    else{                                 // Otherwise...
      Serial.write(byte("?"));            // Tell the Python controller the commmand was unrecognized
    }
  }
  srxErrOut:                              // Serial RX Error Out "safe resume" point

}
