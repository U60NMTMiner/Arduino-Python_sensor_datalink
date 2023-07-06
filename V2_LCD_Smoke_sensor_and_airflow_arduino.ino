//future misc. variable setup
int stop;
unsigned long rightnow;
unsigned long justnow;
unsigned long previousMillis = 0;
unsigned long interval = 1000;               //how often data is sent
String rightnowString;


//flammable gas sensor setup
long smk01;
long smk02;
long smk03;
long smk04;
long smk05;
long smk06;
long smk07;
long smk08;
long smk09;
long smk10;
long smk11;
long smk12;
long smk13;
long smk14;
long smk15;
long smk16;

//air sensor setup
#include <Wire.h>
byte fetch_pressure(unsigned int *p_Pressure);
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

int air00;

//LCD display setup
#include <LiquidCrystal.h>
const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

void setup() {
  Serial.begin(9600);
  pinMode(53, INPUT_PULLUP);                           //pin for button to signal data collection finished

  //airflow sensor setup
  Wire.begin();
  delay(500);

  //fancy lights
  pinMode(22, OUTPUT); //green led
  pinMode(24, OUTPUT); //yellow led
  pinMode(26, OUTPUT); //red led
  digitalWrite(22, HIGH);                            //startup test to make sure no LEDs are burned out
  delay(100);
  digitalWrite(24, HIGH);
  delay(100);
  digitalWrite(26, HIGH);
  delay(100);
  digitalWrite(22, LOW);
  digitalWrite(24, LOW);
  digitalWrite(26, LOW);
  delay(100);
  digitalWrite(22, HIGH);                            //make sure the green LED stays on

  //LCD setup
  lcd.begin(16,2);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("LCD TEST");
  delay(100);
  lcd.print("8888888888888888");
  lcd.setCursor(0, 1);
  lcd.print("8888888888888888");
  delay(250);
  lcd.clear();
  lcd.setCursor(0, 0);

  //Serial calibration stuff, to tell the python code how many sensors are being used

  ////////////////////////////////////MANUALLY add the names and locations of all active sensors here!!!!!//////////////////////////////////////////////////////
  //a sensor is "active" if it is sending data over serial
  Serial.println("S01 S02 S03 S04 S05 S06 S07 S08 S09 S10 S11 S12 S13 S14 S15 S16 A01");             //names of sensors go here
  Serial.println("15 28 7 19 3 12 25 31 10 21 6 30 13 24 5 9 1");                 //get node numbers from https://github.com/sgoodyear/Arduino-Python_sensor_datalink/blob/master/ref.bmp

}


void loop() {
//airflow/pressure sensors
  _status = fetch_pressure(&P_dat, &T_dat);
  switch (_status) {                              //built-in error diagnosis from airflow sensors
    case 0: //Serial.println("Ok ");
      break;
    case 1: //Serial.println("Busy");
      break;
    case 2: //Serial.println("Slate");
      break;
    default: /*Serial.println("Error");*/ digitalWrite(22, LOW); digitalWrite(26, HIGH);
      break;
  }

  rightnow = millis();

  //Serial.println(rightnow / 1000);

  PR = (double)((P_dat - 819.15) / (14744.7));        //math to calibrate airflow sensor data
  PR = (PR - 0.49060678);
  PR = abs(PR);
  V = ((PR * 13789.5144) / 1.225);
  VV = (sqrt((V)));
  Vcor = VV - 7.47;
  TR = (double)((T_dat * 0.09770395701));
  TR = TR - 50;

  ///////////////////////////////Serial outputs (to Python program)////////////////////////////////////////////////

  if (rightnow - previousMillis >= interval && rightnow != justnow) {
    previousMillis = rightnow;
      rightnowString = String(rightnow / 1000); // Convert rightnow to string

  // Pad the string with leading zeros to ensure it is always 5 digits
  while (rightnowString.length() < 5) {
    rightnowString = "0" + rightnowString;
    lcd.setCursor(0, 0);
    lcd.print("....Working....");
    lcd.setCursor(0, 1);
    lcd.print("Timestamp:");
    lcd.setCursor(11, 1);
    lcd.print(rightnowString);
  }



  //Timestamp
    //Serial.print("Ts"); Serial.print(rightnowString); Serial.print(",");
        //not currently using timestamp becasue the serial comms are already being sent in 1-sec intervals
        //  therefore, the index of the data created in python is the 'timestamp'


  //Smoke sensors
    smk01 = analogRead(A0);  //smk01 = map(smk01, 300, 10, 750, 1000000);
    smk02 = analogRead(A1);  //smk02 = map(smk02, 300, 10, 750, 1000000);
    smk03 = analogRead(A2);  //smk03 = map(smk03, 300, 10, 750, 1000000);  //approximate conversion from sensor data to PPM reading
    smk04 = analogRead(A3);  //smk04 = map(smk04, 300, 10, 750, 1000000);
    smk05 = analogRead(A4);  //smk05 = map(smk05, 300, 10, 750, 1000000);  //unfortuantely, doing this causes it to freeze partway
    smk06 = analogRead(A5);  //smk06 = map(smk06, 300, 10, 750, 1000000);  //through line 73...
    smk07 = analogRead(A6);  //smk07 = map(smk07, 300, 10, 750, 1000000);
    smk08 = analogRead(A7);  //smk08 = map(smk08, 300, 10, 750, 1000000);
    smk09 = analogRead(A8);  //smk09 = map(smk09, 300, 10, 750, 1000000);
    smk10 = analogRead(A9);  //smk10 = map(smk10, 300, 10, 750, 1000000);
    smk11 = analogRead(A10); //smk11 = map(smk11, 300, 10, 750, 1000000);
    smk12 = analogRead(A11); //smk12 = map(smk12, 300, 10, 750, 1000000);
    smk13 = analogRead(A12); //smk13 = map(smk13, 300, 10, 750, 1000000);
    smk14 = analogRead(A13); //smk14 = map(smk14, 300, 10, 750, 1000000);
    smk15 = analogRead(A14); //smk15 = map(smk15, 300, 10, 750, 1000000);
    smk16 = analogRead(A15); //smk16 = map(smk16, 300, 10, 750, 1000000);

    //serial data output format:
    //___|_____________
    //first 3 digits: sensor ID
    //everything else: data, no separating characters anywhere

    Serial.print("S01"); Serial.print(smk01); Serial.print(",");
    Serial.print("S02"); Serial.print(smk02); Serial.print(",");
    Serial.print("S03"); Serial.print(smk03); Serial.print(",");
    Serial.print("S04"); Serial.print(smk04); Serial.print(",");
    Serial.print("S05"); Serial.print(smk05); Serial.print(",");
    Serial.print("S06"); Serial.print(smk06); Serial.print(",");
    Serial.print("S07"); Serial.print(smk07); Serial.print(",");
    Serial.print("S08"); Serial.print(smk08); Serial.print(",");
    Serial.print("S09"); Serial.print(smk09); Serial.print(",");
    Serial.print("S10"); Serial.print(smk10); Serial.print(",");
    Serial.print("S11"); Serial.print(smk11); Serial.print(",");
    Serial.print("S12"); Serial.print(smk12); Serial.print(",");
    Serial.print("S13"); Serial.print(smk13); Serial.print(",");
    Serial.print("S14"); Serial.print(smk14); Serial.print(",");
    Serial.print("S15"); Serial.print(smk15); Serial.print(",");
    Serial.print("S16"); Serial.print(smk16); Serial.print(",");

  //Airflow sensors
    //Serial.print("pressure psi:"); Serial.println(PR,10);
    Serial.print("A01"); Serial.print(abs(Vcor)); Serial.print(",");


  //that one analog airflow sensor
    //air00 = analogRead(A8);                                             //optional analog airflow sensor that I found
    //Serial.print("A00"); Serial.println(air00); Serial.print(",");


  //end the serial line to prepare for the next set of data
    Serial.println();
  }

  //killswitch, dump data and create .csv
  stop = digitalRead(53);
  if (stop == LOW) {
    //Serial.println("button press");
    Serial.println("!");
    Serial.println();
    digitalWrite(22, LOW);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Done!");
    while (true) {                                                     //lock the Arduino into an infinite loop until reset
      stop = digitalRead(53);
      if (stop == LOW) {                                                //flashing Y + R LEDs, reminder to depress killswitch to proceed
        delay(500);
        digitalWrite(24, HIGH);
        digitalWrite(26, LOW);
        delay(500);
        digitalWrite(24, LOW);
        digitalWrite(26, HIGH);
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Done!");
      }
      if (stop != LOW) {                                                //flashing Y, ready for user to press reset button
        delay(250);
        digitalWrite(24, HIGH);
        digitalWrite(26, LOW);
        delay(250);
        digitalWrite(24, LOW);
        lcd.setCursor(0, 1);
        lcd.print("Ready to restart");
      }
      //Serial.println("data terminated, reset arduino");
    }
  }

  justnow = rightnow;

}

//getting the data from the airspeed sensor off of the I2C data bus
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
  byte  Temp_L = Wire.read();
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
