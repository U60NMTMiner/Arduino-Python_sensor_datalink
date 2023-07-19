/*//////////////////////////////////////////////////////////////
 * Multiplexer useage:
 * 0x70 ] 1/2 Temp/humidity/pressure sensors
 * 0x71 ] 2/2 Temp/humidity/pressure sensors
 *
 * 0x72 ] undefined
 * 0x73 ] undefined
 * 0x74 ] undefined
 * 0x75 ] undefined
 * 0x76 ] undefined
 * 0x77 ] undefined
 * 
 * 
*///////////////////////////////////////////////////////////////

#include <Wire.h>                // Standard i2c communication library
#include <Adafruit_AHTX0.h>      // Tempurature and humidity sensor library
#include <LiquidCrystal.h>       // Standard LCD display library

byte error = 0;  // Variable for status LEDs
int i = 0;       // Variable for for-loop indexing

float tmps[14]; // Array storage of sensor values. [Assuming 14 sensors]

/* 
 * Technically, there should be 14 sensor initializations for 14 sensors,
 * but since we aren't using the sensors' names to pull data from them,
 * I just define one name and use the multiplex array to select the sensor
 * I want.
 * This method has the added benefit of automatically filling in for
 * missing/broken sensors to prevent errors later.
*/
Adafruit_AHTX0 aht00; // Initialize temperatue sensor(s)

bool stop;                             // stop variable to hold the HIGH/LOW signal from the data dump switch
unsigned long rightnow;                
unsigned long justnow;                 // rightnow/justnow/previousMillis variables to keep track of how long the program has been running
unsigned long previousMillis = 0;
unsigned long interval = 1000;         // interval variable defines how often data is sent (in milliseconds)
//String rightnowString;               // righnowString to optionally timestamp data in the serial stream

long smks[16];                         // Array storage for sensor values
long smkN;                             // Variable to temporarily hold sensor value before it is moved to array
const int smksPins[] = {A0, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, A12, A13, A14, A15};  // Array to hold pins to read

byte fetch_pressure(unsigned int *p_Pressure);  // Setup stuff for the pitot tube airspeed sensor
#define TRUE 1
#define FALSE 0
byte _status;
unsigned int P_dat;
unsigned int T_dat;
double PR;
double TR;
double V;
double VV;
double Vcor;

int air00;                             // Variable to hold data for airspeed sensor

const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;  // Setup stuff for LCD display
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

///////////////////////////////////////////////////////////////////////////////////////////////////////

// Setting up functions for switching between multiplexers
/* 
 * These functions are used for switching which sensor the multiplexer
 * array is talking to, based on their multiplexer's address and the 
 * individual sensor's channel on the multiplexer (1 thru 7).
*/
void TCA70(uint8_t bus){
  if (bus > 7){
    Serial.println(F("Critical Error: Invalid channel number sent to 0x70"));
    while(1);
  }
  MuxRst();

  Wire.beginTransmission(0x70);  // TCA9548A address is 0x70
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}
void TCA71(uint8_t bus){
  if (bus > 7){
    Serial.println(F("Critical Error: Invalid channel number sent to 0x71"));
    while(1);
  }
  MuxRst();

  Wire.beginTransmission(0x71);  // TCA9548A address is 0x71
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}
void TCA72(uint8_t bus){
  if (bus > 7){
    Serial.println(F("Critical Error: Invalid channel number sent to 0x72"));
    while(1);
  }
  MuxRst();

  Wire.beginTransmission(0x72);  // TCA9548A address is 0x72
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}
void TCA73(uint8_t bus){
  if (bus > 7){
    Serial.println(F("Critical Error: Invalid channel number sent to 0x73"));
    while(1);
  }
  MuxRst();

  Wire.beginTransmission(0x73);  // TCA9548A address is 0x73
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}
void TCA74(uint8_t bus){
  if (bus > 7){
    Serial.println(F("Critical Error: Invalid channel number sent to 0x74"));
    while(1);
  }
  MuxRst();

  Wire.beginTransmission(0x74);  // TCA9548A address is 0x74
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}
void TCA75(uint8_t bus){
  if (bus > 7){
    Serial.println(F("Critical Error: Invalid channel number sent to 0x75"));
    while(1);
  }
  MuxRst();

  Wire.beginTransmission(0x75);  // TCA9548A address is 0x75
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}
void TCA76(uint8_t bus){
  if (bus > 7){
    Serial.println(F("Critical Error: Invalid channel number sent to 0x76"));
    while(1);
  }
  MuxRst();

  Wire.beginTransmission(0x76);  // TCA9548A address is 0x76
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}
void TCA77(uint8_t bus){
  if (bus > 7){
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

///////////////////////////////////////////////////////////////////////////////////////////////////////

void setup() {
  Serial.begin(9600);                                      // Begin serial stream
  pinMode(53, INPUT_PULLUP);                               // Set special pinmode for the reset button
  for(int i = 0; i <= 15; i++){
    pinMode(smksPins[i], INPUT);                           // Set pinmodes for all analog pins
  }

  delay(100);
  Serial.println(F("Serial connection to PC initialized"));  //(F()) saves string to flash & keeps dynamic memory free
  Wire.begin();
  delay(100);
  Serial.println(F("i2c bus initialized"));
  Serial.println(F("Performing AHT20 startup test..."));
  
  delay(20); // Sensors need 20ms to initialize after powerup

  Serial.println();
  Serial.println(F("Multiplexer 0x70:"));
  for(int i = 0; i <= 7; i++){
    //Serial.println(i);
    TCA70(i);    // Set multiplexer "00" to channel "i"
    delay(10);
    if (! aht00.begin()) {
      Serial.print("! Could not find AHT20 on 0x70/ch"); Serial.println(i);
    }
    else{
      Serial.print("AHT20 0x70/ch"); Serial.print(i); Serial.println(" active");
    }
    delay(50);
  }

  delay(100);

  Serial.println();
  Serial.println(F("Multiplexer 0x71:"));
  for(int i = 0; i <= 7; i++){
    //Serial.println(i);
    TCA71(i);    // Set multiplexer "01" to channel "i"
    delay(10);
    if (! aht00.begin()) {
      Serial.print("! Could not find AHT20 on 0x71/ch"); Serial.println(i);
    }
    else{
      Serial.print("AHT20 0x71/ch"); Serial.print(i); Serial.println(" active");
    }
    delay(50);
  }
  
  Serial.println("Data to follow:")
}
