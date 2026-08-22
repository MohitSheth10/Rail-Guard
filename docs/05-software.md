[← Back to main README](../README.md)

# Software

Firmware lives in [`firmware/`](../firmware/). Analysis lives in
[`analysis/`](../analysis/).

---

## Where it is

Component bring-up is done. The accelerometer captures cleanly at a verified
1000 Hz. Nothing yet turns that data into a decision — that's the work now.

## The 1 kHz capture sketch

[`firmware/mpu6050_1khz_capture/`](../firmware/mpu6050_1khz_capture/)

Samples the accelerometer at 1000 Hz for a fixed burst, buffers it in RAM, dumps it
as CSV, then reports on its own timing.

**Why 1000 Hz.** That's the accelerometer's hardware ceiling. The gyro on the same
chip runs at 8 kHz, but the accelerometer refreshes its registers exactly 1000 times
a second. Reading faster returns the same numbers again, which adds nothing and
corrupts an FFT.

**Getting there from 2 Hz** took four fixes, all of them necessary:

1. I2C bus to 400 kHz — the 100 kHz default has no headroom
2. Enable the DLPF for a 1 kHz internal base rate, then `SMPLRT_DIV = 0`
3. Absolute-deadline scheduling instead of `delay()`, so error doesn't accumulate
4. Buffer the whole burst and print afterwards — printing during capture silently
   wrecks the timing while leaving data that looks fine

**It proves its own timing.** Every run ends with a report:

```
achieved rate (Hz) : 1000.xxx
rate error (%)     : x.xxx
  min / max / mean / std interval (us)
dropped/short reads: 0
VERDICT: PASS
```

FAIL if the rate is more than 2% off, if any interval runs 50% over the mean, or if
a read dropped. The point is not to take the sample rate on trust.

**Two guards** worth knowing about:

- Startup reads `WHO_AM_I` and refuses to run on an unrecognised chip. It accepts
  the 6050 (`0x68`), 6500 (`0x70`) and 9250 (`0x71`), and prints which one it found
- A compile-time check catches the ESP32-S3 USB setting that sends `Serial` out the
  UART pins and leaves the Serial Monitor silently blank

There's also an I2C bus scan at startup, which is the fastest way to tell a wiring
fault from a configuration one.

## Earlier test sketch

[`firmware/mpu6050_basic_test/`](../firmware/mpu6050_basic_test/) — the original
bring-up sketch. Reads the accelerometer twice a second and prints it. Useless for
vibration, but it's the right first thing to run when checking whether a sensor is
alive at all. Kept for that.

## Analysis

[`analysis/natural_frequency.py`](../analysis/natural_frequency.py) — section
properties and beam frequency from measured dimensions. Working explained in
[06-theory.md](06-theory.md).

---

## What's next

### Small tasks

- Verify the HX711 reads the load cell
- Calibrate the load cell against known weights
- Confirm data over GPIO 4 / 5

### Main tasks, in order

1. **Convert MPU data to a frequency.** Capture a burst to SD, pull it onto a
   laptop, get the FFT right in Python where it can be plotted and checked, then
   port the working method to the ESP32. Debugging signal processing through serial
   prints on a microcontroller is slow and miserable.

2. **Tight vs loose.** Define exactly what "loose" means — how many turns of the
   spanner — then run the cart 10 times tight and 10 times loose, logging every
   run. Plot both. Write down the two averages and the gap between them. If there's
   no gap, change one variable and go again.

3. **Pick a threshold** that separates the two.

4. **Auto-trigger.** Detect the cart arriving from the vibration spike and use that
   to start the frequency calculation, rather than triggering by hand.

5. **LED indicator.** On for loose, off for tight. Run the cart 10 times and count
   how many it gets right. That score is the Phase 1 result.

### Then Phase 2

Load cell and HX711 — get a raw reading, calibrate, log force alongside frequency,
run both together.

Phases 3 (dataset and ML) and 4 (GPS) are out of scope for now.

---

[← Electronics](04-electronics.md) · [Theory →](06-theory.md)
