// DO NOT CONNECT THE ESP32 TO 12V!

// Attach simulation rig's 5v to to pin VUSB
// Connect the fan's ground wires (BLACK and BROWN) to Ground


const int frontfan = D4;  // Attach GREEN to "D4"
const int rearfan = D6;   // Attach YELLOW to "D6"

const int potPin1 = A2;  // Potentiometer 1 to pin "D2"
const int potPin2 = A3;  // Potentiometer 2 to pin "D3"



void setup() {
  Serial.begin(115200);

  // Set up PWM channels
  ledcSetup(1, 25000, 8);  // channel 1, 25000 Hz, 8-bit resolution
  ledcSetup(2, 25000, 8);  // channel 2, 25000 Hz, 8-bit resolution

  // Attach PWM channels to fan speed control pins
  ledcAttachPin(frontfan, 1);
  ledcAttachPin(rearfan, 2);

  // Set initial fan speed to zero
  ledcWrite(frontfan, 0);
  ledcWrite(rearfan, 0);


  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on

  // Read potentiometers
  int potValue1 = analogRead(potPin1);
  int potValue2 = analogRead(potPin2);

  // Remap potentiometer input signal range to PWM ouput signal range
  int frontfanrpm = map(potValue2, 0, 4095, 255, 5);
  int rearfanrpm = map(potValue1, 0, 4095, 255, 5);

  Serial.print(potValue1);
  Serial.print(" ");
  Serial.println(potValue2);

  Serial.print(frontfanrpm);
  Serial.print(" ");
  Serial.println(rearfanrpm);

  // Update fan speed
  ledcWrite(1, frontfanrpm);
  ledcWrite(2, rearfanrpm);

  delay(10);
}
