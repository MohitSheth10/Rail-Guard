# Rail-Guard

**IBDP Extended Project — Mohit Sheth**

Rail-Guard is an embedded safety system for model railways that detects derailments in real time using an IMU sensor and automatically cuts motor power before the train leaves the track.

---

## The Experience

This project pushed me well outside my comfort zone — and that was the point.

I came in knowing Python, but Rail-Guard required me to think across two very different worlds at the same time: the software side (writing embedded C++ for the ESP32, training a basic ML classifier) and the hardware side (soldering components onto a PCB, reading spec sheets, debugging with a multimeter). Those two worlds don't always cooperate, and figuring out where a bug lives — is it the code, the wiring, or the sensor? — taught me a kind of systematic thinking I hadn't needed before.

The hardware was the steepest learning curve. Getting the MPU-6050 gyroscope to return clean, consistent data meant understanding I²C communication, calibration drift, and noise — concepts I'd never touched. Wiring the L298N motor driver correctly (and understanding *why* ENA/ENB needed to be bridged) came from reading datasheets rather than tutorials. That shift — going to primary technical documentation — felt like a real step forward.

By the end, I had a much deeper appreciation for how software actually runs in the physical world. Timing matters. Power matters. A line of code that works perfectly in simulation can behave completely differently when a real motor is drawing current on the same supply rail.

---

## What It Does

- Reads motion data from an MPU-6050 IMU at 100 Hz
- Classifies the motion pattern as normal or derailment using a trained threshold model
- Triggers the L298N motor driver to cut power within milliseconds of detection
- Logs all events to a MicroSD card with timestamps

---

## Hardware

| Component | Role |
|---|---|
| ESP32-S3 Zero | Main microcontroller |
| MPU-6050 (GY-521) | Gyroscope / accelerometer |
| L298N Motor Driver | Controls track motor power |
| MicroSD Module | Event logging |
| XY3606 Buck Converter | Stable 5V supply |

---

## Repository Structure

```
Rail-Guard/
├── code/               # Arduino sketches and ML training notes
├── docs/               # Project logbook and report
├── hardware/           # Circuit schematic, BOM, block diagram
├── media/              # Photos and demo videos
├── presentations/      # Pitch deck
└── specification_sheets/  # Component datasheets
```

---

## Status

Hardware assembled and tested. Derailment detection working on bench. Next phase: refine ML classifier with larger training dataset and package electronics into a compact enclosure.
