#include <SPI.h>
#include <mcp2515.h>
#include <CD74HC4067.h>

struct can_frame canData;   // Structure for sending data
struct can_frame canStatus; // Structure for signaling end of data
struct can_frame canMsg;    // Structure for incomming messages
MCP2515 mcp(53);
bool go = false;

CD74HC4067 muxC(6, 5, 4, 3);  // Telling the library where to find the analog multiplexer control pins
CD74HC4067 muxD(11, 10, 9, 8);

int rnum;
int count = 0;

float RawWind;
float AmbientTemp;
float Vref_wind = 1.25;  // Voltage that the sensor puts out when covered by a cup
                         // You may need to adjust the potentiometer if the voltage is different
float WS_MPH;
float WS_M_S;            // Variable to temporarily hold each sensor's data
float wss[23];            // Array  for storing 23 sensors' data

// Function to convert an long integer into 4 bytes
byte databytes[4];
void I2B(long value, byte* bytes) {
  // Break the integer into 4 bytes
  bytes[0] = (value >> 24) & 0xFF;
  bytes[1] = (value >> 16) & 0xFF;
  bytes[2] = (value >> 8) & 0xFF;
  bytes[3] = value & 0xFF;
}

void setup() {
  canData.can_id  = 0x41;  // This ID tag is hex for "A"
  canData.can_dlc = 4;
  canData.data[3];

  canStatus.can_id = 0x5E;   // Character "^" to define a status message
  canStatus.can_dlc = 1;
  canStatus.data[0] = canData.can_id;

  Serial.begin(1000000);
  
  mcp.reset();
  mcp.setBitrate(CAN_1000KBPS, MCP_8MHZ);
  mcp.setNormalMode();
  delay(100);

  pinMode(A0, INPUT);
  pinMode(A1, INPUT);

  for (byte i = 2; i <= 13; i ++){
    pinMode(i, OUTPUT);                                         // Set all digital control pins to outputs
  }

  digitalWrite(13, HIGH);
}

void loop() {
  if (mcp.readMessage(&canMsg) == MCP2515::ERROR_OK) {
    if (canMsg.can_id == 0x7E && canMsg.can_dlc == 2){          // Listen for startup ping from master control unit
      mcp.sendMessage(&canStatus);                              // send back status
      delay(10);
      Serial.println("ACK sent to master's ping (A)");
      Serial.println();
    }
    else if (canMsg.can_id == 0x7E && canMsg.can_dlc == 1){     // Listen for "Go" message from master control
      go = true;
      for(int i = 0; i <= 15; i ++){                            // Read data from the multiplexers first
        muxC.channel(i);                                        // Set channel # (0 -> 15)
        muxD.channel(i);
        RawWind = analogRead(A0)  * 5.0 / 1023.0;               // 5/1023 is the correction from raw data to voltage
        AmbientTemp = analogRead(A1) * 5.0 / 1023.0;
        AmbientTemp = (AmbientTemp - 0.400) / 0.0195;           // Temperatue calibration equation provided by manufacturer
        WS_MPH = constrain( pow(((RawWind - Vref_wind)/(3.038517 * (pow(AmbientTemp, 0.115157))))/0.087288,3.009364), 0, 100);  // Airspeed calibration provided by manufacturer
        if (isnan(WS_MPH)){                                     // If Vref_wind < RawWind, the above formula spits out "NaN" ("Not a Number")
          WS_MPH = 0;                                           // When this happens, replace it with 0
          //Serial.println("NaN corrected");
        }
        WS_M_S = WS_MPH * 0.44704;                              // Conversion from mph to m/s
        wss[i] = WS_MPH;                                        // Store data in array
      }

      RawWind = analogRead(A2)  * 5.0 / 1023.0;                 // Next, read the sensors connected directly
      AmbientTemp = analogRead(A3) * 5.0 / 1023.0;
      AmbientTemp = (AmbientTemp - 0.400) / 0.0195;             // Temperatue calibration equation provided by manufacturer
      WS_MPH = constrain( pow(((RawWind - Vref_wind)/(3.038517 * (pow(AmbientTemp, 0.115157))))/0.087288,3.009364), 0, 100);  // Airspeed calibration provided by manufacturer
      if (isnan(WS_MPH)){                                       // If Vref_wind < RawWind, the above formula spits out "NaN" ("Not a Number")
        WS_MPH = 0;                                             // When this happens, replace it with 0
        //Serial.println("NaN corrected");
      }
      WS_M_S = WS_MPH * 0.44704;                                // Conversion from mph to m/s
      wss[16] = WS_MPH;                                         // Store data in array

      RawWind = analogRead(A4)  * 5.0 / 1023.0;
      AmbientTemp = analogRead(A5) * 5.0 / 1023.0;
      AmbientTemp = (AmbientTemp - 0.400) / 0.0195;             // Temperatue calibration equation provided by manufacturer
      WS_MPH = constrain( pow(((RawWind - Vref_wind)/(3.038517 * (pow(AmbientTemp, 0.115157))))/0.087288,3.009364), 0, 100);  // Airspeed calibration provided by manufacturer
      if (isnan(WS_MPH)){                                       // If Vref_wind < RawWind, the above formula spits out "NaN" ("Not a Number")
        WS_MPH = 0;                                             // When this happens, replace it with 0
        //Serial.println("NaN corrected");
      }
      WS_M_S = WS_MPH * 0.44704;                                // Conversion from mph to m/s
      wss[17] = WS_MPH;                                         // Store data in array

      RawWind = analogRead(A6)  * 5.0 / 1023.0;
      AmbientTemp = analogRead(A7) * 5.0 / 1023.0;
      AmbientTemp = (AmbientTemp - 0.400) / 0.0195;             // Temperatue calibration equation provided by manufacturer
      WS_MPH = constrain( pow(((RawWind - Vref_wind)/(3.038517 * (pow(AmbientTemp, 0.115157))))/0.087288,3.009364), 0, 100);  // Airspeed calibration provided by manufacturer
      if (isnan(WS_MPH)){                                       // If Vref_wind < RawWind, the above formula spits out "NaN" ("Not a Number")
        WS_MPH = 0;                                             // When this happens, replace it with 0
        //Serial.println("NaN corrected");
      }
      WS_M_S = WS_MPH * 0.44704;                                // Conversion from mph to m/s
      wss[18] = WS_MPH;                                         // Store data in array

      RawWind = analogRead(A8)  * 5.0 / 1023.0;
      AmbientTemp = analogRead(A9) * 5.0 / 1023.0;
      AmbientTemp = (AmbientTemp - 0.400) / 0.0195;             // Temperatue calibration equation provided by manufacturer
      WS_MPH = constrain( pow(((RawWind - Vref_wind)/(3.038517 * (pow(AmbientTemp, 0.115157))))/0.087288,3.009364), 0, 100);  // Airspeed calibration provided by manufacturer
      if (isnan(WS_MPH)){                                       // If Vref_wind < RawWind, the above formula spits out "NaN" ("Not a Number")
        WS_MPH = 0;                                             // When this happens, replace it with 0
        //Serial.println("NaN corrected");
      }
      WS_M_S = WS_MPH * 0.44704;                                // Conversion from mph to m/s
      wss[19] = WS_MPH;                                         // Store data in array

      RawWind = analogRead(A10)  * 5.0 / 1023.0;
      AmbientTemp = analogRead(A11) * 5.0 / 1023.0;
      AmbientTemp = (AmbientTemp - 0.400) / 0.0195;             // Temperatue calibration equation provided by manufacturer
      WS_MPH = constrain( pow(((RawWind - Vref_wind)/(3.038517 * (pow(AmbientTemp, 0.115157))))/0.087288,3.009364), 0, 100);  // Airspeed calibration provided by manufacturer
      if (isnan(WS_MPH)){                                       // If Vref_wind < RawWind, the above formula spits out "NaN" ("Not a Number")
        WS_MPH = 0;                                             // When this happens, replace it with 0
        //Serial.println("NaN corrected");
      }
      WS_M_S = WS_MPH * 0.44704;                                // Conversion from mph to m/s
      wss[20] = WS_MPH;                                         // Store data in array

      RawWind = analogRead(A12)  * 5.0 / 1023.0;
      AmbientTemp = analogRead(A13) * 5.0 / 1023.0;
      AmbientTemp = (AmbientTemp - 0.400) / 0.0195;             // Temperatue calibration equation provided by manufacturer
      WS_MPH = constrain( pow(((RawWind - Vref_wind)/(3.038517 * (pow(AmbientTemp, 0.115157))))/0.087288,3.009364), 0, 100);  // Airspeed calibration provided by manufacturer
      if (isnan(WS_MPH)){                                       // If Vref_wind < RawWind, the above formula spits out "NaN" ("Not a Number")
        WS_MPH = 0;                                             // When this happens, replace it with 0
        //Serial.println("NaN corrected");
      }
      WS_M_S = WS_MPH * 0.44704;                                // Conversion from mph to m/s
      wss[21] = WS_MPH;                                         // Store data in array

      RawWind = analogRead(A14)  * 5.0 / 1023.0;
      AmbientTemp = analogRead(A15) * 5.0 / 1023.0;
      AmbientTemp = (AmbientTemp - 0.400) / 0.0195;             // Temperatue calibration equation provided by manufacturer
      WS_MPH = constrain( pow(((RawWind - Vref_wind)/(3.038517 * (pow(AmbientTemp, 0.115157))))/0.087288,3.009364), 0, 100);  // Airspeed calibration provided by manufacturer
      if (isnan(WS_MPH)){                                       // If Vref_wind < RawWind, the above formula spits out "NaN" ("Not a Number")
        WS_MPH = 0;                                             // When this happens, replace it with 0
        //Serial.println("NaN corrected");
      }
      WS_M_S = WS_MPH * 0.44704;                                // Conversion from mph to m/s
      wss[22] = WS_MPH;                                         // Store data in array


      // The airspeed sensors should be the fastest, so they get to send their data first!
      for(int i = 0; i < 23; i++){                // For all 23 air velocity sensors...
        Serial.print(wss[i], 4);
        Serial.print(" = ");
        I2B(long(wss[i] * 10000), databytes);      // Convert data from floats to bytes...
        for(int o = 0; o < 4; o++){               // (Need 4 bytes to hold all data)
          canData.data[o] = databytes[o];         // Put data (as 4 bytes) into the CAN message...
          Serial.print(canData.data[o], BIN);
          Serial.print(" ");
        }
        Serial.println();
        mcp.sendMessage(&canData);                // And send the message
        delay(7);                                 // Mandatory delay (minimum 4 ms)
      }
      mcp.sendMessage(&canStatus);              // Then send terminator to signal end of data
      delay(10);
      Serial.println("Data sent over CAN");
      Serial.println();
      go = false;
    }
  }
}
