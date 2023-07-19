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


/* Technically, there should be 14 sensor initializations for 14 sensors,
 * but since we aren't using the sensors' names to pull data from them,
 * I just define one name and use the multiplex array to select the sensor
 * I want.
 * This method has the added benefit of automatically filling in for
 * missing/broken sensors to prevent errors later.  */
Adafruit_AHTX0 aht00; // Initialize temperatue sensor(s)

bool stop;                             // stop variable to hold the HIGH/LOW signal from the data dump switch
unsigned long rightnow;                
unsigned long justnow;                 // rightnow/justnow/previousMillis variables to keep track of how long the program has been running
unsigned long previousMillis = 0;
unsigned long interval = 1000;         // interval variable defines how often data is sent (in milliseconds)
String rightnowString;                 // righnowString to timestamp data for the LCD screen (and optionally for serial)

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

//float airs[14]                             // Array to hold data for airspeed sensor

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

// Function to get the data from the airspeed sensor off of the I2C data bus
byte fetch_pressure(unsigned int *p_P_dat, unsigned int *p_T_dat) {
  byte address, Press_H, Press_L, _status;
  unsigned int P_dat;
  unsigned int T_dat;
  address = 0x28;
  Wire.beginTransmission(address);
  Wire.endTransmission();
  delay(10);
  Wire.requestFrom((int)address, (int) 4); //Request 4 bytes need 4 bytes are read
  Press_H = Wire.read();
  Press_L = Wire.read();
  byte Temp_H = Wire.read();
  byte Temp_L = Wire.read();
  Wire.endTransmission();
  _status = (Press_H >> 6) & 0x03;
  Press_H = Press_H & 0x3f;
  P_dat = (((unsigned int)Press_H) << 8) | Press_L;
  *p_P_dat = P_dat;
  Temp_L = (Temp_L >> 5);
  T_dat = (((unsigned int)Temp_H) << 3) | Temp_L;
  *p_T_dat = T_dat;
  return (_status);
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void setup() {
  Serial.begin(115200);                                    // Begin serial stream
  pinMode(53, INPUT_PULLUP);                               // Set special pinmode for the reset button
  for(int i = 0; i <= 15; i++){
    pinMode(smksPins[i], INPUT);                           // Set pinmodes for all analog pins
  }

  delay(100);
  Serial.println(F("Serial connection to PC initialized"));  //(F()) saves string to flash & keeps dynamic memory free
  Wire.begin();
  delay(100);
  Serial.println(F("i2c bus initialized"));

// AHT 20 temperature/humidity sensor startup tests
  /* This section of the code cycles through the channels of the first 2 multiplexers (0x70 and 0x71)
   * looking for connected AHT20 sensors.
  */
  Serial.println(F("Performing AHT20 startup test..."));
  delay(20);                                                                          // Sensors need 20ms to initialize after powerup

  Serial.println(F("Multiplexer 0x70:"));
  for(int i = 0; i <= 7; i++){                                                        // 8 sensors on 0x70
    TCA70(i);                                                                         // Set multiplexer 0x70 to channel "i"
    delay(10);
    if (! aht00.begin()) {                                                            // Check for a response from any of the AHT20 sensors
      Serial.print("! Disconnected AHT20 on 0x70/ch"); Serial.println(i);
    }
    else{
      Serial.print("AHT20 0x70/ch"); Serial.print(i); Serial.println(" active");
    }
    delay(50);
  }
  delay(100);
  Serial.println(F("Multiplexer 0x71:"));
  for(int i = 0; i <= 5; i++){                                                        // 6 sensors on 0x71
    TCA71(i);                                                                         // Set multiplexer 0x71 to channel "i"
    delay(10);
    if (! aht00.begin()) {
      Serial.print("! Disconnected AHT20 on 0x71/ch"); Serial.println(i);
    }
    else{
      Serial.print("AHT20 0x71/ch"); Serial.print(i); Serial.println(" active");
    }
    delay(50);
  }
  for(int i = 6; i <= 7; i++){                                                        // Make sure no extras are unintentionally plugged in
    TCA71(i);
    delay(10);
    if (! aht00.begin()) {
      Serial.print("AHT20 0x71/ch"); Serial.print(i); Serial.println(" empty");
    }
    else{
      Serial.print("! Unexpected AHT20 on 0x71/ch"); Serial.println(i);
    }
    delay(50);
  }
  Serial.println(F("AHT20 Startup complete"));
  Serial.println();

// LCD Display startup
  /* This section puts characters onto all of 32 sections of the LCD screen to make
   * sure that none of the segments are burned out. 
  */
  lcd.begin(16,2);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("LCD TEST");
  delay(100);
  lcd.clear();
  delay(100);
  lcd.print("8888888888888888");
  lcd.setCursor(0, 1);
  lcd.print("8888888888888888");
  delay(400);
  lcd.clear();
  lcd.setCursor(0, 0);
  Serial.println(F("LCD Display starting"));

// LED indicator light startup
  pinMode(22, OUTPUT); //green led
  pinMode(24, OUTPUT); //yellow led
  pinMode(26, OUTPUT); //red led
  digitalWrite(22, HIGH);                            //startup test to make sure no LEDs are burned out
  delay(300);
  digitalWrite(24, HIGH);
  delay(300);
  digitalWrite(26, HIGH);
  delay(300);
  digitalWrite(22, LOW);
  digitalWrite(24, LOW);
  digitalWrite(26, LOW);
  delay(300);
  digitalWrite(22, HIGH);                            //make sure the green LED stays on at the end



// Once all the setup data is printed to serial for the user to read,
  /* this line signals to the Python program that it is about to start 
   * getting the data it cares about.
  */
  Serial.println();
  Serial.println(F("Data to follow:"));



  // Serial calibration stuff, to tell the python code how many sensors are being used
////////////////////////////////////MANUALLY add the names and locations of all active sensors here!!!!!//////////////////////////////////////////////////////
  // A sensor is "active" if it is sending data over serial
  Serial.print(F("S01 S02 S03 S04 S05 S06 S07 S08 S09 S10 S11 S12 S13 S14 S15 S16"));        //names of sensors go here
  Serial.print(F(" A01"));
  Serial.print(F(" T01 T02 T03 T04 T05 T06 T07 T08 T09 T10 T11 T12 T13 T14"));
  Serial.println();

  Serial.print(F("23 14 7 19 3 12 25 31 10 21 6 30 13 24 5 9"));     //get node numbers from https://github.com/sgoodyear/Arduino-Python_sensor_datalink/blob/master/ref.bmp
  Serial.print(F(" 1"));
  Serial.print(F(" 29 23 22 20 10 17 6 2 8 10 13 24 27 30"));
  Serial.println();


  //Serial.println("S01 S02 A01");             //names of sensors go here
  //Serial.println("23 14 1");                 //get node numbers from https://github.com/sgoodyear/Arduino-Python_sensor_datalink/blob/master/ref.bmp

// Setting persistent LCD elements so that they don't have to be repeated every loop
  lcd.setCursor(0, 0);
  lcd.print("....Working....");
  lcd.setCursor(0, 1);
  lcd.print("Timestamp:");
}

void loop() {
  rightnow = millis();
  if (rightnow - previousMillis >= interval && rightnow != justnow) {
    previousMillis = rightnow;
    rightnowString = String(rightnow / 1000); // Convert rightnow to string for the LCD to display

    while (rightnowString.length() < 5) {
      rightnowString = "0" + rightnowString;    // Pad the string with leading zeros to ensure it is always 5 digits.
    }                                           // This ensures it will always properly fit on the LCD display.
      lcd.setCursor(11, 1);
      lcd.print(rightnowString);


    // Timestamp
      //Serial.print("Ts"); Serial.print(rightnowString); Serial.print(",");
          // Not currently using timestamp becasue the serial comms are already being sent in 1-sec intervals.
          // Therefore, the index of the data created in python is the 'timestamp.'

    // Smoke sensors
      for(int i = 0; i <= 15; i++){                                     // Reads all 16 analog gas sensors in 3 lines instead of 16
        smkN = constrain(analogRead(smksPins[i]), 250, 800);
        smks[i] = constrain(map(smkN, 250, 800, 0, 10000), 0, 10000);   // Map function gives readings as approximate PPMs
      }

      for (int i = 0; i <= 15; i++) {
        Serial.print("S");
        if (i < 9) {
          Serial.print("0");                                              // Add leading zero for single-digit sensor IDs
        }
        Serial.print(i + 1);                                              // Print the sensor ID (there is no sensor 0)
        Serial.print(smks[i]); Serial.print(",");                         // Print the sensor's data
      }

    // Airflow sensors
      _status = fetch_pressure(&P_dat, &T_dat);       // Get readings from the sensor
      switch (_status) {                              // Built-in error diagnosis sent from sensor
        case 0: //Serial.println("Ok ");
          break;
        case 1: //Serial.println("Busy");
          break;
        case 2: //Serial.println("Slate");
          break;
        default: /*Serial.println("Error");*/ digitalWrite(22, LOW); digitalWrite(26, HIGH); // If there is an error, set status LED to red
          break;
      }
      PR = (double)((P_dat - 819.15) / (14744.7));        // Math to interpret airflow sensor data
      PR = (PR - 0.49060678);
      PR = abs(PR);
      V = ((PR * 13789.5144) / 1.225);
      VV = (sqrt((V)));
      Vcor = VV - 7.47 -5;
      TR = (double)((T_dat * 0.09770395701));
      TR = TR - 50;
      Serial.print("A01"); Serial.print(abs(Vcor)); Serial.print(",");    // While there is only one airspeed sensor no need for a for-loop


    // Temperature sensors
    for(int i = 0; i <= 7; i++){
      TCA70(i);                                          // Change multiplexer 0x70 to channel "i"
      sensors_event_t humidity, temp;                    // Tell the sensors to get data
      aht00.getEvent(&humidity, &temp);                  // Tell the sensors to send theie data
      tmps[i] = temp.temperature;                        // Store the data in the temperature data array
    }

    for(int i = 8; i <= 15; i++){
      TCA71(i - 8);                                      // Set multiplexer 0x71 to channel "i-8" to compensate for different loop start position
      sensors_event_t humidity, temp;                    // Tell the sensors to get data
      aht00.getEvent(&humidity, &temp);                  // Tell the sensors to send their data
      tmps[i] = temp.temperature;                        // Store the data in the temperature data array
    }
    for (int i = 0; i <= 14; i++) {
        Serial.print("T");
        if (i < 9) {
          Serial.print("0");                             // Add leading zero for single-digit sensor IDs
        }
        Serial.print(i + 1);                             // Print the sensor ID (there is no sensor 0)
        Serial.print(tmps[i]); Serial.print(",");        // Print the sensor's data
      }


    // End the serial line to prepare for the next set of data
      Serial.println();
    }                                                                     // End of the if statement that runs every interval (default every 1 second)




    // Killswitch
    stop = digitalRead(53);                                               // At the end of each loop, the program checks the state of the switch
    if (stop == LOW) {
      Serial.println("!");                                                // If the button is pressed, send the "end of data" indicator...
      Serial.println();
      digitalWrite(22, LOW);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Done!");
      lcd.setCursor(11, 0);
      lcd.print(rightnowString);
      while (true) {                                                      // ...and then lock the Arduino into an infinite loop
        stop = digitalRead(53);
        if (stop == LOW) {                                                // Flashing Y + R LEDs, reminder to depress killswitch to proceed
          delay(500);
          digitalWrite(24, HIGH);
          digitalWrite(26, LOW);
          delay(500);
          digitalWrite(24, LOW);
          digitalWrite(26, HIGH);
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Done!");
          lcd.setCursor(11, 0);
          lcd.print(rightnowString);
        }
        if (stop != LOW) {                                                // Flashing Y LED, ready for user to press reset button
          delay(250);
          digitalWrite(24, HIGH);
          digitalWrite(26, LOW);
          delay(250);
          digitalWrite(24, LOW);
          lcd.setCursor(0, 1);
          lcd.print("Ready to restart");
        }
      }
    }

    justnow = rightnow;                                                  // Update time since the time interval loop last ran
  }
