#include <SPI.h>
#include <mcp2515.h>

struct can_frame canData;   // Structure for sending data
struct can_frame canStatus; // Structure for signaling end of data
struct can_frame canMsg;    // Structure for incomming messages
MCP2515 mcp(53);

int rnum;
int count = 0;



void setup() {
  canData.can_id  = 0x53;
  canData.can_dlc = 1;
  canData.data[0];

  canStatus.can_id = 0x5E;
  canStatus.can_dlc = 1;
  canStatus.data[0] = canData.can_id;

  
  while (!Serial);
  Serial.begin(1000000);
  
  mcp.reset();
  mcp.setBitrate(CAN_1000KBPS, MCP_8MHZ);
  mcp.setNormalMode();
  delay(100);


  Serial.println("Example: Write to CAN");

  for(int u = 0; u <= 255; u ++){
    byte(rnum) = count;
    Serial.println(rnum, BIN);
    canData.data[0] = rnum;
    count ++;
    mcp.sendMessage(&canData);
    delay(1);
  }
  mcp.sendMessage(&canStatus);

  Serial.println("Messages sent");
}

void loop() {
  if (mcp.readMessage(&canMsg) == MCP2515::ERROR_OK) {
    if (canMsg.can_id == 0x7E && canMsg.can_dlc == 2){   // Listen for a message from master control unit
      mcp.sendMessage(&canStatus);  // send back status
      Serial.println("ACK sent to master's ping (S)");
    }
  }
}
