#include <SPI.h>
#include <mcp2515.h>

struct can_frame canStatus;
struct can_frame canMsg;
MCP2515 mcp2515(53);


void setup() {
  canStatus.can_id = 0x5E;
  canStatus.can_dlc = 1;
  canStatus.data[0] = 0x53;    //Arduino's future ID tag

  Serial.begin(1000000);
  mcp2515.reset();
  mcp2515.setBitrate(CAN_1000KBPS, MCP_8MHZ);
  mcp2515.setNormalMode();
  delay(100);
  
  //Serial.println("------- CAN Read ----------");
  //Serial.println("ID  DLC  DATA");
}

void loop() {
  if (mcp2515.readMessage(&canMsg) == MCP2515::ERROR_OK) {
    if (canMsg.can_id == 0x7E && canMsg.can_dlc == 2){   // Listen for a message from master control unit
      mcp2515.sendMessage(&canStatus);  // send back status
      Serial.println("ACK sent to master's ping");
    }

    //Serial.print(canMsg.can_id, HEX); // print ID as hex
    Serial.print(char(canMsg.can_id));  // Print ID as character
    Serial.print(" "); 
    Serial.print(canMsg.can_dlc, HEX); // print DLC
    Serial.print(" ");
    
    if (canMsg.can_id == 0x5E){
      Serial.print(char(canMsg.data[0]));
      Serial.print(" ");
    }
    else{
      for (int i = 0; i<canMsg.can_dlc; i++)  {  // print the data
        Serial.print(canMsg.data[i], BIN);
        Serial.print(" ");
      }
    }

    Serial.println();      
  }
}
