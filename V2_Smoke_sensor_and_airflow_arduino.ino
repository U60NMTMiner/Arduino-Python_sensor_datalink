//future misc. variable setup
int stop;                
unsigned long rightnow;                              

//flammable gas sensor setup
int smk01;                                             
int smk02;
int smk03;
int smk04;
int smk05;
int smk06;
int smk07;
int smk08;

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


void setup() {
  Serial.begin(600);
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


//Serial calibration stuff, to tell the python code how many sensors are being used
  Serial.println("A01 S01 S02");///////////////////////MANUALLY add the names of all active sensors here!!!!!///////////////////////////
//                                                   //a sensor is "active" if it is sending data over serial

}

void loop() {
//airflow/pressure sensors
  while (1){                                         //built-in error diagnosis from airflow sensors
    _status = fetch_pressure(&P_dat, &T_dat);
    switch (_status){
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
    Serial.println(rightnow / 1000);

    PR = (double)((P_dat-819.15)/(14744.7)) ;        //math to calibrate airflow sensor data
    PR = (PR - 0.49060678) ;
    PR = abs(PR);
     V = ((PR*13789.5144)/1.225);
    VV = (sqrt((V)));
    Vcor = VV - 7.47;
    TR = (double)((T_dat*0.09770395701));
    TR = TR-50;
    
  
//Serial outputs (to Python program)

  //Airflow sensors
    //Serial.print("pressure psi:"); Serial.println(PR,10);
    Serial.print("A01"); Serial.print(abs(Vcor)); Serial.print(",");

  //Smoke sensors
  smk01 = analogRead(A0);
  smk02 = analogRead(A1);
  smk03 = analogRead(A2);
  smk04 = analogRead(A3);
  smk05 = analogRead(A4);
  smk06 = analogRead(A5);

  Serial.print("S01"); Serial.print(smk01); Serial.print(",");
  Serial.print("S02"); Serial.print(smk02); Serial.print(",");
  ///*Serial.print("S03");*/ Serial.print(smk02); Serial.print(",");    //serial data output format:
  ///*Serial.print("S04");*/ Serial.print(smk03); Serial.print(",");    //___|_____________
  ///*Serial.print("S05");*/ Serial.print(smk04); Serial.print(",");    //first 3 digits: sensor ID
  ///*Serial.print("S06");*/ Serial.print(smk05); Serial.print(",");    //everything else: data, no separating characters anywhere

//that one analog airflow sensor
  //air00 = analogRead(A8);                                             //optional analog airflow sensor that I found
  //Serial.print("A00"); Serial.println(air00); Serial.print(",");


//end the serial line to prepare for the next set of data
    Serial.println();

//killswitch, dump data and create .csv
    stop = digitalRead(53);
    if(stop == LOW) {
      //Serial.println("button press");
      Serial.println("!");
      digitalWrite(22, LOW);
      while (true){                                                     //lock the Arduino into an infinite loop until reset
      stop = digitalRead(53);
        if(stop == LOW){                                                //flashing Y + R LEDs, reminder to depress killswitch to proceed
        delay(500);
        digitalWrite(24, HIGH);
        digitalWrite(26, LOW);
        delay(500);
        digitalWrite(24, LOW);
        digitalWrite(26, HIGH);
        }
        if(stop != LOW){                                                //flashing Y, ready for user to press reset button
          delay(250);
          digitalWrite(24, HIGH);
          digitalWrite(26, LOW);
          delay(250);
          digitalWrite(24, LOW);
        }
        //Serial.println("data terminated, reset arduino");
       }
      }
    }
}


//getting the data from the airspeed sensor off of the I2C data bus
byte fetch_pressure(unsigned int *p_P_dat, unsigned int *p_T_dat){
  byte address, Press_H, Press_L, _status;
  unsigned int P_dat;
  unsigned int T_dat;
  address = 0x28;
  Wire.beginTransmission(address);
  Wire.endTransmission();
  delay(10);
  Wire.requestFrom((int)address, (int) 4);//Request 4 bytes need 4 bytes are read
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
