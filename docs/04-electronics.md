[← Back to main README](../README.md)

# Electronics

---

## Components

| Part | Role |
|---|---|
| Waveshare ESP32-S3 Zero | Main controller |
| MPU-6050 / GY-521 | Accelerometer — the primary sensor |
| HX711 | Load cell amplifier (Phase 2) |
| Load cell | Bolt clamping force (Phase 2, not yet connected) |
| MicroSD card module | Logging raw captures |
| L298N motor driver | Drives the cart / vibration motor |
| XY3606 | Power module |
| LED | Detection indicator |

Datasheets for all of these are in the project folder under `Specification Sheets`.

## Pin map

| Signal | Pin |
|---|---|
| MPU SDA | GPIO 8 |
| MPU SCL | GPIO 9 |
| HX711 DT / SCK | GPIO 4 / GPIO 5 |

I2C runs at 400 kHz, not the 100 kHz Arduino default. At 1000 samples a second
there isn't enough time in a millisecond to move six bytes over a 100 kHz bus with
any margin.

The MPU was originally wired to GPIO 6 and 7 — the earlier test sketch still shows
that. It moved to 8 and 9 during the high-rate work.

![ESP32-S3 Zero pinout](../media/img/esp32-s3-zero-pinout.png)

## Board note

The chip on the GY-521 board reports `WHO_AM_I = 0x70`, which makes it an
**MPU-6500**, not an MPU-6050. They're sold interchangeably. Mostly
register-compatible, but the accelerometer's low-pass filter lives in a different
register on each, so the firmware writes both and identifies the chip at startup.

Slight bonus: the 6500's widest accelerometer bandwidth is 460 Hz where the 6050's
is 260 Hz. More usable range.

## Assembly

Everything is soldered onto perfboard rather than breadboarded — vibration testing
and jumper wires don't mix.

![Bare board and headers](../media/gif/soldering-pcb.gif)

![Assembled PCB](../media/img/pcb-assembled-bench-01.jpg)

![Assembled circuit](../media/img/circuit-assembled.jpg)

The HX711 is soldered in place but nothing is connected on its load-cell side yet.
That's a Phase 2 job.

## Schematic

![Schematic](../media/img/schematic-diagram.jpg)

![Block diagram](../media/img/block-diagram.png)

Editable wiring diagram (`.drawio`) and the full schematic PDFs are in the project
folder under `Final Schematic` and `Block Diagram`.

## Test status

| Component | Status |
|---|---|
| ESP32-S3 | Tested — heartbeat sketch passes |
| MPU accelerometer | Tested — reads correctly, verified 1000 Hz |
| MicroSD module | Tested — reads and writes |
| HX711 | **Not tested** |
| Motor driver | **Not tested** |
| Load cell | **Not connected** |

## Outstanding

- Connect motor with twisted wire (twisting the pair cuts the noise it throws into
  the accelerometer lines)
- Connect load cell to HX711
- Improve cart wiring, add a switch
- Photograph the final wiring and record every pin before something comes loose

---

[← Build](03-build.md) · [Software →](05-software.md)
