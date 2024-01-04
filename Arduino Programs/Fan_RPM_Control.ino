const int s1fan = 4;  // Attach GREEN to "D4"
const int s2fan = 5;  // Attach YELLOW to "D5"

const int potPin1 = A2;  // Potentiometer 1 to pin "D2"
const int potPin2 = A3;  // Potentiometer 2 to pin "D3"

LEDC ledc1;
LEDC ledc2;

void setup() {
  // Set up PWM channels
  ledc1.setup(1, 25000, 8);  // channel 1, 25000 Hz, 8-bit resolution
  ledc2.setup(2, 25000, 8);  // channel 2, 25000 Hz, 8-bit resolution

  // Attach PWM channels to fan speed control pins
  ledc1.attachPin(s1fan);
  ledc2.attachPin(s2fan);

  // Set initial fan speed to zero
  ledc1.write(0);
  ledc2.write(0);
}

void loop() {
  // Read potentiometers
  int potValue1 = analogRead(potPin1);
  int potValue2 = analogRead(potPin2);

  // Remap potentiometer input signal range to PWM ouput signal range
  int s1rpm = map(potValue1, 0, 1023, 0, 255);
  int s2rpm = map(potValue2, 0, 1023, 0, 255);

  // Update fan speed
  ledc1.write(s1rpm);
  ledc2.write(s2rpm);

  delay(10);
}
