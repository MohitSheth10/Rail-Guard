#include <Wire.h>

#define SDA_PIN 6
#define SCL_PIN 7
#define MPU_ADDR 0x68

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Starting MPU-6050 test...");

  Wire.begin(SDA_PIN, SCL_PIN);

  // Wake up MPU-6050
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);
  Wire.write(0x00);
  byte error = Wire.endTransmission(true);

  if (error == 0) {
    Serial.println("MPU-6050 found and connected!");
  } else {
    Serial.println("MPU-6050 NOT found. Check your wiring.");
  }
}

void loop() {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, 6, true);

  int16_t ax = Wire.read() << 8 | Wire.read();
  int16_t ay = Wire.read() << 8 | Wire.read();
  int16_t az = Wire.read() << 8 | Wire.read();

  Serial.print("X: "); Serial.print(ax);
  Serial.print("  Y: "); Serial.print(ay);
  Serial.print("  Z: "); Serial.println(az);

  delay(500);
}
