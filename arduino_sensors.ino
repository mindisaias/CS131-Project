#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_TSL2591.h>

// Create TSL2591 sensor object
Adafruit_TSL2591 tsl = Adafruit_TSL2591(2591);

// Pin definitions
const int pirPin = 2;        // PIR sensor input pin
const int redPin = 9;        // RGB LED red pin
const int greenPin = 10;     // RGB LED green pin
const int bluePin = 11;      // RGB LED blue pin

void setup() {
  Serial.begin(9600);

  pinMode(pirPin, INPUT);
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);

  if (tsl.begin()) {
    Serial.println("TSL2591 connected.");
  } else {
    Serial.println("Could not connect to TSL2591. Check wiring!");
    while (1);
  }

  // Configure sensor gain and integration time
  tsl.setGain(TSL2591_GAIN_MED);
  tsl.setTiming(TSL2591_INTEGRATIONTIME_100MS);
}

// Function to set RGB LED color (values 0-255)
void setRGB(int r, int g, int b) {
  analogWrite(redPin, r);
  analogWrite(greenPin, g);
  analogWrite(bluePin, b);
}

void loop() {
  // Read PIR motion sensor (HIGH if motion detected)
  int motionDetected = digitalRead(pirPin);

  // Read ambient light sensor lux value
  sensors_event_t event;
  tsl.getEvent(&event);
  float lightLevel = event.light;

  // Send sensor data to Jetson Nano over serial: "motion,light\n"
  Serial.print(motionDetected);
  Serial.print(",");
  Serial.println(lightLevel);

  // Check if Jetson sent a command 
  if (Serial.available()) {
    char command = Serial.read();

    switch(command) { 

      case '0': // Turn LED off
        setRGB(0, 0, 0);
        break;
      case '1': // Warm orange
        setRGB(255, 100, 0);
        break;
      case '2': // Cool blue
        setRGB(0, 100, 255);
        break;
      case '3': // Soft white
        setRGB(200, 200, 200);
        break;
      // Add more commands as needed
    }
  }

  delay(500); // 0.5 sec delay between readings
}
