#include <SPI.h>
#include <SD.h>

#define SD_CS_PIN 10

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Initializing SD card...");

  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("SD card initialization failed!");
    while (true);
  }
  Serial.println("SD card initialized successfully.");

  File myFile = SD.open("test.txt", FILE_WRITE);
  if (myFile) {
    myFile.println("Hello from Rail-Guard!");
    myFile.close();
    Serial.println("Write successful.");
  } else {
    Serial.println("Error opening file.");
  }
}

void loop() {}
