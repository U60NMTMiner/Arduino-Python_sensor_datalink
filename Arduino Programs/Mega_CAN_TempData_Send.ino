#include <Wire.h>                // Standard i2c communication library
#include <Adafruit_AHTX0.h>      // Tempurature and humidity sensor library
#include <CD74HC4067.h>

byte error = 0;  // Variable for status LEDs

float tmps[128]; // Array storage of sensor values. [Assuming 89 sensors]


/* Technically, there should be 89 sensor initializations for 89 sensors,
 * but since we aren't using the sensors' names to pull data from them,
 * I just define one name and use the multiplex array to select the sensor
 * I want.
 * This method has the added benefit of automatically filling in for
 * missing/broken sensors to prevent errors later.  */
Adafruit_AHTX0 aht00; // Initialize temperatue sensor(s)

bool stop;                             // stop variable to hold the HIGH/LOW signal from the data dump switch

#include <SPI.h>
#include <mcp2515.h>
struct can_frame canData;   // Structure for sending data
struct can_frame canStatus; // Structure for signaling end of data
struct can_frame canMsg;    // Structure for incomming messages
MCP2515 mcp(53);
bool go = false;

CD74HC4067 muxE(4, 5, 6, 7);  // Telling the library where to find the multiplexer control pins
CD74HC4067 muxF(11, 10, 9, 8);

///////////////////////////////////////////////////////////////////////////////////////////////////////
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


// Setting up functions for switching between multiplexers
/* 
 * These functions are used for switching which sensor the multiplexer
 * array is talking to, based on their multiplexer's address and the 
 * individual sensor's channel on the multiplexer (1 thru 7).
*/
void TCA70(uint8_t bus){
  if (bus > 7 || bus < 0){
    Serial.println(F("Critical Error: Invalid channel number sent to 0x70"));
    while(1);
  }
  MuxRst();
  Wire.beginTransmission(0x70);  // TCA9548A address is 0x70
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}
void TCA71(uint8_t bus){
  if (bus > 7 || bus < 0){
    Serial.println(F("Critical Error: Invalid channel number sent to 0x71"));
    while(1);
  }
  MuxRst();
  Wire.beginTransmission(0x71);  // TCA9548A address is 0x71
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}
void TCA72(uint8_t bus){
  if (bus > 7 || bus < 0){
    Serial.println(F("Critical Error: Invalid channel number sent to 0x72"));
    while(1);
  }
  MuxRst();
  Wire.beginTransmission(0x72);  // TCA9548A address is 0x72
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}
void TCA73(uint8_t bus){
  if (bus > 7 || bus < 0){
    Serial.println(F("Critical Error: Invalid channel number sent to 0x73"));
    while(1);
  }
  MuxRst();
  Wire.beginTransmission(0x73);  // TCA9548A address is 0x73
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}
void TCA74(uint8_t bus){
  if (bus > 7 || bus < 0){
    Serial.println(F("Critical Error: Invalid channel number sent to 0x74"));
    while(1);
  }
  MuxRst();
  Wire.beginTransmission(0x74);  // TCA9548A address is 0x74
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}
void TCA75(uint8_t bus){
  if (bus > 7 || bus < 0){
    Serial.println(F("Critical Error: Invalid channel number sent to 0x75"));
    while(1);
  }
  MuxRst();
  Wire.beginTransmission(0x75);  // TCA9548A address is 0x75
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}
void TCA76(uint8_t bus){
  if (bus > 7 || bus < 0){
    Serial.println(F("Critical Error: Invalid channel number sent to 0x76"));
    while(1);
  }
  MuxRst();
  Wire.beginTransmission(0x76);  // TCA9548A address is 0x76
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}
void TCA77(uint8_t bus){
  if (bus > 7 || bus < 0){
    Serial.println(F("Critical Error: Invalid channel number sent to 0x77"));
    while(1);
  }
  MuxRst();
  Wire.beginTransmission(0x77);  // TCA9548A address is 0x77
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}

/*
 * Sean's MuxRst() Function:
 * 
 * This custom function is neccesary to prevent the multiplexers from
 * freaking out when you have a channel already open on one of them, and
 * then try to open a channel on a different one.
 * When called, this function closes all channels on all multiplexers.
 * 
 * MuxRst() is included in the above functions for switching channels.
*/
void MuxRst(){
  Wire.beginTransmission(0x70);
  Wire.write(0);
  Wire.endTransmission();
  Wire.beginTransmission(0x71);
  Wire.write(0);
  Wire.endTransmission();
  Wire.beginTransmission(0x72);
  Wire.write(0);
  Wire.endTransmission();
  Wire.beginTransmission(0x73);
  Wire.write(0);
  Wire.endTransmission();
  Wire.beginTransmission(0x74);
  Wire.write(0);
  Wire.endTransmission();
  Wire.beginTransmission(0x75);
  Wire.write(0);
  Wire.endTransmission();
  Wire.beginTransmission(0x76);
  Wire.write(0);
  Wire.endTransmission();
  Wire.beginTransmission(0x77);
  Wire.write(0);
  Wire.endTransmission();
}

// Function to loop through every sensor on the array
void TCAScan(String scantype){ // Use "Ping" or "Scan"
  if(scantype == "Ping"){
    for(int a = 0; a < 2; a ++){
      muxE.channel(a + 14);
      muxF.channel(a + 14);
      for(int i = 0; i <= 7; i++){
        TCA70(i);                 
        delay(10);
        if (! aht00.begin()) {    
          Serial.print("! Disconnected AHT20 on 0x70/ch"); Serial.println(i);
        }
        else{
          Serial.print("AHT20 0x70/ch"); Serial.print(i); Serial.println(" active");
        }
        delay(10);
      }
      for(int i = 0; i <= 7; i++){
        TCA71(i);                 
        delay(10);
        if (! aht00.begin()) {    
          Serial.print("! Disconnected AHT20 on 0x71/ch"); Serial.println(i);
        }
        else{
          Serial.print("AHT20 0x71/ch"); Serial.print(i); Serial.println(" active");
        }
        delay(10);
      }
      for(int i = 0; i <= 7; i++){
        TCA72(i);                 
        delay(10);
        if (! aht00.begin()) {    
          Serial.print("! Disconnected AHT20 on 0x72/ch"); Serial.println(i);
        }
        else{
          Serial.print("AHT20 0x72/ch"); Serial.print(i); Serial.println(" active");
        }
        delay(10);
      }
      for(int i = 0; i <= 7; i++){
        TCA73(i);                 
        delay(10);
        if (! aht00.begin()) {    
          Serial.print("! Disconnected AHT20 on 0x73/ch"); Serial.println(i);
        }
        else{
          Serial.print("AHT20 0x73/ch"); Serial.print(i); Serial.println(" active");
        }
        delay(10);
      }
      for(int i = 0; i <= 7; i++){
        TCA74(i);                 
        delay(10);
        if (! aht00.begin()) {    
          Serial.print("! Disconnected AHT20 on 0x74/ch"); Serial.println(i);
        }
        else{
          Serial.print("AHT20 0x74/ch"); Serial.print(i); Serial.println(" active");
        }
        delay(10);
      }
      for(int i = 0; i <= 7; i++){
        TCA75(i);                 
        delay(10);
        if (! aht00.begin()) {    
          Serial.print("! Disconnected AHT20 on 0x75/ch"); Serial.println(i);
        }
        else{
          Serial.print("AHT20 0x75/ch"); Serial.print(i); Serial.println(" active");
        }
        delay(10);
      }
      for(int i = 0; i <= 7; i++){
        TCA76(i);                 
        delay(10);
        if (! aht00.begin()) {    
          Serial.print("! Disconnected AHT20 on 0x76/ch"); Serial.println(i);
        }
        else{
          Serial.print("AHT20 0x76/ch"); Serial.print(i); Serial.println(" active");
        }
        delay(10);
      }
      for(int i = 0; i <= 7; i++){
        TCA77(i);                 
        delay(10);
        if (! aht00.begin()) {    
          Serial.print("! Disconnected AHT20 on 0x77/ch"); Serial.println(i);
        }
        else{
          Serial.print("AHT20 0x77/ch"); Serial.print(i); Serial.println(" active");
        }
        delay(10);
      }
    }
  }
  else if(scantype == "Scan"){
    for(int a = 0; a < 2; a ++){
      muxE.channel(a + 14);
      muxF.channel(a + 14);
      for(int i = 0; i <= 7; i++){
        TCA70(i);                 
        sensors_event_t humidity, temp;                    // Tell the sensors to get data
        aht00.getEvent(&humidity, &temp);                  // Tell the sensors to send theie data
        tmps[i + (a * 64)] = temp.temperature;             // Store the data in the temperature data array
      }
      for(int i = 0; i <= 7; i++){
        TCA71(i);                 
        sensors_event_t humidity, temp;  
        aht00.getEvent(&humidity, &temp);
        tmps[(i + 1 + (7 * 1)) + (a * 64)] = temp.temperature;      
      }
      for(int i = 0; i <= 7; i++){
        TCA72(i);                 
        sensors_event_t humidity, temp;  
        aht00.getEvent(&humidity, &temp);
        tmps[(i + 2 + (7 * 2)) + (a * 64)] = temp.temperature;  
      }
      for(int i = 0; i <= 7; i++){
        TCA73(i);                 
        sensors_event_t humidity, temp;  
        aht00.getEvent(&humidity, &temp);
        tmps[(i + 3 + (7 * 3)) + (a * 64)] = temp.temperature;  
      }
      for(int i = 0; i <= 7; i++){
        TCA74(i);                 
        sensors_event_t humidity, temp;  
        aht00.getEvent(&humidity, &temp);
        tmps[(i + 4 + (7 * 4)) + (a * 64)] = temp.temperature;
      }
      for(int i = 0; i <= 7; i++){
        TCA75(i);                 
        sensors_event_t humidity, temp;  
        aht00.getEvent(&humidity, &temp);
        tmps[(i + 5 + (7 * 5)) + (a * 64)] = temp.temperature;
      }
      for(int i = 0; i <= 7; i++){
        TCA76(i);                 
        sensors_event_t humidity, temp;  
        aht00.getEvent(&humidity, &temp);
        tmps[(i + 6 + (7 * 6)) + (a * 64)] = temp.temperature;
      }
      for(int i = 0; i <= 7; i++){
        TCA77(i);                 
        sensors_event_t humidity, temp;  
        aht00.getEvent(&humidity, &temp);
        tmps[(i + 7 + (7 * 7)) + (a * 64)] = temp.temperature;
      }
    }
  }
  else{
    Serial.println("Error, invalid scan type parameter.");
    while(true);
  }
}
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void setup() {
  canData.can_id  = 0x54;
  canData.can_dlc = 4;
  canData.data[3];

  canStatus.can_id = 0x5E;
  canStatus.can_dlc = 1;
  canStatus.data[0] = canData.can_id;

  Serial.begin(1000000);                                   // Begin serial stream

  delay(100);
  Serial.println(F("Serial connection to PC initialized"));  //(F()) saves string to flash & keeps dynamic memory free

  mcp.reset();
  mcp.setBitrate(CAN_1000KBPS, MCP_8MHZ);
  mcp.setNormalMode();
  delay(100);
  Serial.println(F("CAN Connection initialized"));

  Wire.begin();
  delay(100);
  Serial.println(F("i2c bus initialized"));

  pinMode(48, INPUT_PULLUP);                               // Set  pinmode for the reset button

// AHT 20 temperature/humidity sensor startup tests
  /* This section of the code cycles through the channels of the first 2 multiplexers (0x70 and 0x71)
   * looking for connected AHT20 sensors.
  */
  Serial.println(F("Performing AHT20 startup test..."));
  delay(20);                                                                          // Sensors need 20ms to initialize after powerup

  TCAScan("Ping");
  delay(100);
  
  Serial.println(F("AHT20 Startup complete"));
  Serial.println();
}

void loop() {
  if (mcp.readMessage(&canMsg) == MCP2515::ERROR_OK) {
    if (canMsg.can_id == 0x7E && canMsg.can_dlc == 2){   // Listen for startup ping from master control unit
      mcp.sendMessage(&canStatus);                       // send back status
      delay(10);
      Serial.println("ACK sent to master's ping (T)");
      Serial.println();
    }
    else if (canMsg.can_id == 0x7E && canMsg.can_dlc == 1){  // Listen for "Go" message from master control
      go = true;
      // Read temperature sensors
      /* From: https://files.seeedstudio.com/wiki/Grove-AHT20_I2C_Industrial_Grade_Temperature_and_Humidity_Sensor/AHT20-datasheet-2020-4-16.pdf
      *  Section 5.4.3 says that each sensor takes 80ms to make a measurement. I am not sure if that is handled by the library,
      *  but it seems to work just fine without extra delays in the code. Still, it will take longer and longer to read everything
      *  the more sensors you add.
      */ 
      TCAScan("Scan");
      for(int i = 0; i < 89; i ++){
        Serial.print(tmps[i]);
        Serial.print(" ");
      }
      Serial.println();
    }
    else if (canMsg.can_id == 0x5E && canMsg.data[0] == 0x53 && go == true){  // go=True condition to prevent spamming after Master's ping
      delay(5);
      for (int i = 0; i < 89; i++){
        I2B(long(tmps[i] * 10000), databytes);
        for(int o = 0; o < 4; o++){
          canData.data[o] = databytes[o];
          Serial.print(databytes[o], BIN);
          Serial.print(" ");
        }
        Serial.println();
        mcp.sendMessage(&canData);
        delay(7);
        Serial.flush();
      }
      
      mcp.sendMessage(&canStatus);              // Then send terminator to signal end of data
      delay(7);
      Serial.println("Data sent over CAN");
      Serial.println();
      go = false;
    }
  }

    // Killswitch
    stop = digitalRead(48);                                 // At the end of each loop, the program checks the state of the switch
    if (stop == LOW) {
      Serial.println("!");                                                // If the button is pressed, send the "end of data" indicator...
      mcp.sendMessage(&canStatus);
      Serial.println();
      digitalWrite(22, LOW);
      while (true) {                                                      // ...and then lock the Arduino into an infinite loop
        stop = digitalRead(48);
        if (stop == LOW) {                                                // Flashing Y + R LEDs, reminder to depress killswitch to proceed
          delay(500);
          digitalWrite(24, HIGH);
          digitalWrite(26, LOW);
          delay(500);
          digitalWrite(24, LOW);
          digitalWrite(26, HIGH);
        }
        if (stop != LOW) {                                                // Flashing Y LED, ready for user to press reset button
          delay(250);
          digitalWrite(24, HIGH);
          digitalWrite(26, LOW);
          delay(250);
          digitalWrite(24, LOW);

        }
      }
    }

}
