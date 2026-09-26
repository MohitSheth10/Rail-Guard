/* =============================================================================
 *  mpu6050_1khz_stream.ino
 *
 *  Rail bolt-looseness detector - CONTINUOUS vibration streaming.
 *  Board : Waveshare ESP32-S3 Zero (Arduino framework, ESP32 core)
 *  Sensor: MPU-6500 (GY-521, WHO_AM_I=0x70), I2C addr 0x68, SDA=GPIO8, SCL=GPIO9
 *
 *  HOW THIS DIFFERS FROM mpu6050_1khz_capture.ino
 *    That sketch buffers a fixed 2-second burst into RAM, then dumps it once and
 *    stops (useful for the one-time timing proof). This sketch instead prints
 *    every sample AS IT IS TAKEN, forever - so a PC logger (daq.py) can record
 *    continuously for as long as you like, until you close it.
 *
 *    Same validated config as the capture sketch: 1000 Hz (the accelerometer's
 *    hardware max), +/-8g range, correct MPU-6500 filter register. See
 *    mpu6050_1khz_capture.ino for the full explanation of every setting - this
 *    file keeps the comments short and focuses on what's different.
 *
 *  OUTPUT FORMAT (one line per sample, matches daq.py's expected format):
 *    sample_index,micros,ax,ay,az
 *
 *  WHY NOT BUFFER-THEN-DUMP FOR THIS USE CASE
 *    Printing costs time, so printing DURING sampling adds a little jitterx
 *    compared to the buffer-then-dump approach. But for "record until I say
 *    stop" there is no fixed-size buffer that would work - you don't know in
 *    advance how long you'll run. The absolute-deadline scheduler below still
 *    keeps each sample's read within a few microseconds of its ideal instant,
 *    which is far tighter than anything an FFT of rail-impact vibration needs.
 * ========================================================================== */

#include <Wire.h>

#if defined(ARDUINO_USB_MODE) && (ARDUINO_USB_MODE == 0) && \
    (!defined(ARDUINO_USB_CDC_ON_BOOT) || (ARDUINO_USB_CDC_ON_BOOT == 0))
#error "Serial will not work over USB. In Tools set 'USB CDC On Boot' -> Enabled. The included sketch.yaml sets this for you."
#endif

/* ----------------------- USER-TUNABLE CONSTANTS -------------------------- */
static const int      SDA_PIN  = 8;    // GY-521 SDA -> GPIO 8
static const int      SCL_PIN  = 9;    // GY-521 SCL -> GPIO 9
static const uint8_t  MPU_ADDR = 0x68;
static const uint32_t I2C_HZ   = 400000;

static const uint32_t TARGET_RATE_HZ   = 1000;                       // accel hardware max
static const uint32_t SAMPLE_PERIOD_US = 1000000UL / TARGET_RATE_HZ; // 1000 us

// Full-scale range: 0x00=+/-2g 0x08=+/-4g 0x10=+/-8g 0x18=+/-16g
static const uint8_t ACCEL_FS_SEL = 0x10;     // +/-8g (avoids clipping on impacts)

// Accel DLPF (MPU-6500: ACCEL_CONFIG2 0x1D). 0x00 = widest bandwidth (460 Hz).
static const uint8_t GYRO_DLPF_CFG  = 0x01;   // CONFIG 0x1A: enables 1 kHz internal base rate
static const uint8_t ACCEL_DLPF_CFG = 0x00;   // ACCEL_CONFIG2 0x1D: widest accel bandwidth
static const uint8_t SMPLRT_DIV_VALUE = 0;    // 1000 / (1+0) = 1000 Hz

/* --------------------------- MPU REGISTERS -------------------------------- */
static const uint8_t REG_SMPLRT_DIV    = 0x19;
static const uint8_t REG_CONFIG        = 0x1A;
static const uint8_t REG_ACCEL_CONFIG  = 0x1C;
static const uint8_t REG_ACCEL_CONFIG2 = 0x1D;
static const uint8_t REG_ACCEL_XOUT_H  = 0x3B;   // burst-read start: accel(6B) only
static const uint8_t REG_PWR_MGMT_1    = 0x6B;
static const uint8_t REG_WHO_AM_I      = 0x75;

/* ============================ I2C HELPERS ================================ */
static bool writeReg(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);
  Wire.write(val);
  return Wire.endTransmission(true) == 0;
}

static uint8_t readReg(uint8_t reg) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, (uint8_t)1, (uint8_t)true);
  return Wire.read();
}

static inline bool readAccel(int16_t &ax, int16_t &ay, int16_t &az) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(REG_ACCEL_XOUT_H);
  Wire.endTransmission(false);
  uint8_t n = Wire.requestFrom(MPU_ADDR, (uint8_t)6, (uint8_t)true);
  if (n != 6) return false;
  ax = (int16_t)((Wire.read() << 8) | Wire.read());
  ay = (int16_t)((Wire.read() << 8) | Wire.read());
  az = (int16_t)((Wire.read() << 8) | Wire.read());
  return true;
}

static void halt(const char *msg) {
  Serial.print(F("[FATAL] "));
  Serial.println(msg);
  while (true) { delay(1000); }
}

/* ============================ SETUP ======================================= */
void setup() {
  Serial.begin(115200);
  delay(1500);

  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(I2C_HZ);

  Serial.println(F("\n=== MPU 1 kHz CONTINUOUS stream ==="));

  uint8_t who = readReg(REG_WHO_AM_I);
  const char *chip = (who == 0x68) ? "MPU-6050"
                    : (who == 0x70) ? "MPU-6500"
                    : (who == 0x71) ? "MPU-9250" : nullptr;
  if (chip == nullptr) {
    halt("Unknown WHO_AM_I -- check wiring on GPIO8/9 and 3.3V power.");
  }
  Serial.print(F("Sensor: ")); Serial.print(chip);
  Serial.print(F("  (WHO_AM_I=0x")); Serial.print(who, HEX); Serial.println(F(")"));

  if (!writeReg(REG_PWR_MGMT_1, 0x01))              halt("Failed to write PWR_MGMT_1.");
  delay(50);
  if (!writeReg(REG_CONFIG, GYRO_DLPF_CFG))         halt("Failed to write CONFIG.");
  if (!writeReg(REG_ACCEL_CONFIG, ACCEL_FS_SEL))    halt("Failed to write ACCEL_CONFIG.");
  if (!writeReg(REG_ACCEL_CONFIG2, ACCEL_DLPF_CFG)) halt("Failed to write ACCEL_CONFIG2.");
  if (!writeReg(REG_SMPLRT_DIV, SMPLRT_DIV_VALUE))  halt("Failed to write SMPLRT_DIV.");
  delay(50);

  Serial.println(F("Streaming at 1000 Hz. Format: sample_index,micros,ax,ay,az"));
  Serial.println(F("This never stops on its own - close daq.py / press RST to end.\n"));
  Serial.println(F("sample_index,micros,ax,ay,az"));   // header, once
}

/* ====================== CONTINUOUS STREAMING LOOP ========================= *
 * Same absolute-deadline scheduler as the burst-capture sketch: sample i is   *
 * due at t0 + i*PERIOD, so a slightly-late print doesn't push later samples   *
 * late too. No delay() anywhere in this loop.                                 */
static uint32_t t0 = 0;
static uint32_t i  = 0;

// Live rate readout: prints an [info]-style line every RATE_CHECK_EVERY
// samples so you can watch the ACTUAL achieved rate on screen in real time,
// without needing to analyze the CSV afterward. daq.py already ignores any
// line that isn't pure comma-separated integers, so this line is shown on
// screen but never written into the CSV.
static const uint32_t RATE_CHECK_EVERY = 2000;   // ~every 2 s at 1000 Hz
static uint32_t lastCheckI = 0;
static uint32_t lastCheckT = 0;

void loop() {
  if (t0 == 0) { t0 = micros(); lastCheckT = t0; }   // first call: start the clock

  const uint32_t deadline = t0 + i * SAMPLE_PERIOD_US;
  while ((int32_t)(micros() - deadline) < 0) { /* busy-wait */ }

  int16_t ax, ay, az;
  const uint32_t t = micros();
  if (!readAccel(ax, ay, az)) { ax = ay = az = 0; }   // dropped read -> sentinel

  Serial.print(i);       Serial.print(',');
  Serial.print(t);       Serial.print(',');
  Serial.print(ax);      Serial.print(',');
  Serial.print(ay);      Serial.print(',');
  Serial.println(az);

  i++;

  if (i - lastCheckI >= RATE_CHECK_EVERY) {
    const double rate = (double)(i - lastCheckI) * 1000000.0 / (double)(t - lastCheckT);
    Serial.print(F("# rate check: "));
    Serial.print(rate, 1);
    Serial.println(F(" Hz (target 1000.0)"));
    lastCheckI = i;
    lastCheckT = t;
  }
}
