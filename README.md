# V4 System
## Overview
The latest iteration of this project, V4, has many differences from the V3 release. In order to accommodate over 200 sensors, the task of collecting data is split between 3 Arduino Mega 2560 microcontrollers and a Raspberry Pi single-board computer. To enable communication between the 4 devices, they are connected to a CAN ([Controller Area Network](en.wikipedia.org/wiki/CAN_bus)) bus. After collecting data from all of the sensors, the V4 Python program running on the Raspberry Pi sorts it into a spreadsheet. From there, the [Mine_Evacuation.py](https://github.com/sgoodyear/Arduino-Python_sensor_datalink/blob/master/Mine_Evacuation.py) program reads the spreadsheet and generates the optimal escape route.

## Arduino Load Splitting
With so many sensors, a single Arduino Mega does not have the available pins, memory, or processing power to collect data from all of them. Therefore, 3 Arduino Megas are being used to collect data from each of the 3 types of sensors. One Arduino is responsible for collecting data from all 23 of the air velocity sensors, one collects data from all the MQ-2 gas sensors, and one collects data from all of the AHT20 temperature sensors. Even in this arrangement, the Arduino Mega does not have enough pins to connect to all of the sensors directly. To solve this issue, each Arduino is connected to an array of multipliexers that allow one analog pin (or 1 i2c bus) to collect data from over 100 sensors.

## CAN Bus Communication
A 2-wire CAN bus is the heart of this project since it is how all 4 of the devices communicate and corrdinate data collection. To begin the process, the V4 Python program on the Raspberry Pi sends the "Go" signal over the CAN bus (using the Arduino Nano as an intermediate) which tells all of the Arduino Mega microcontrollers to begin collecting data from all of the sensors. To help simplify the V4 python program, the Arduinos send their data in the same order every time. To begin, the airspeed sensor Arduino sends its data over the CAN bus first (as soon as their data is collected). Since all of the Arduinos connected to the CAN bus can read all of the messagees that are sent, the Arduino connected to the MQ-2 gas sensors waits until the airspeed data termination message is broadcasted before it sends its data. Similarly, the Arduino connected to the AHT20 temperature sensors waits until the gas data termination message is broadcasted before it sends its data.

This order (Airspeed, Gas, Temperature) was chosen because of the amount of time it takes the Arduinos to collect data from each type of sensor. The airspeed is first because their Arduino only has to make 46 analog read operations (2 for each airspeed sensor), then gas requires 93 analog read operations (1 for each gas sensor), then the temperature requires 172 commands sent over the i2c bus (2 commands per sensor) plus an 80ms internal delay for each connected sensor. Since all of the Arduinos begin data collection process simultaneously, this ensures that they are ready for the next "Go" signal as quickly as possible.

As for the individual messages that each Arduino sends, each one contains an ID and 4 bytes of data. On startup, each Arduino assigns itself a unique ID character (A, S, T, and ~) based on its role. Since the maximum amount of data that can be sent in a message is 8 bytes, the float or long integer results of the sensor readings are converted into 4 bytes of binary data. Each message that is broadcasted over the CAN bus contains the data from one sensor, and after all of the messages are sent, the Arduino sends a termination signal using the termination ID (" ^ "), and using it's unique ID ("A","S", or "T") as the message. The V4 Python program will convert the data from byte form back into its orignal float form or long integer form based on the type of data it is.

### CAN Bus Example
The code used by the Arduino Nano to pass on the "Go" signal from the Raspberry Pi, using an [mcp2515.h library](https://github.com/autowp/arduino-mcp2515):
```
  canGo.can_id = 0x7E;                        // Using the master controller ID "~" in HEX
  canGo.can_dlc = 1;                          // Specify just one byte of data will be sent
  canGo.data[0] = byte("G");                  // "Go" signal
```

## Power
The data collection section of this project is powered entirely by a MeanWell 150 Watt power supply. Plugged into US wall power at 120vAC, it outpts 24vDC at up to 6.5 amps. For safety, a [3D printed cover](https://github.com/sgoodyear/Arduino-Python_sensor_datalink/blob/master/3D%20Models/Power%20Supply%20Terminal%20Cover%20v1.3mf) was added to cover up the exposed power terminals. At the output of the power supply, two xt-60 connectors and 1 deans (aka "t-plug") connector are available to split the output between
* An LM2596 buck converter to supply 5v to the Raspberry Pi
* A generic brand 24v to 12v buck converter to supply power to the airspeed sensors
* A raw 24v output

Instead of stepping 24v down to 5v at the power supply and running a 6 AWG cable to send power to the Arduinos and 5v sensors, a much smaller 12AWG cable sends 24v to several smaller buck converters to supply 5v to small groups of components. As an additional safety measure, the 24v to 12v converter has an xt-60 connector on the 24 volt side and an xt-90 connector on the 12 volt side to ensure it will not be connected backwards.
