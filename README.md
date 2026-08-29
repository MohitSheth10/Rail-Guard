# Rail-Guard 🚆

### Finding loose railway bolts by listening to how the track shakes.

**IBDP Extended Project — Mohit Sheth**

Railway joints are held together by fishplates and bolts. Trains repeatedly pass over them, the joint vibrates, and over time a bolt can start to loosen.

I wanted to know whether that change could be detected from the vibration of the rail itself.

So I built a small railway joint, put an accelerometer on it, added a motor to create repeatable vibration, and started collecting data.

That became **Rail-Guard**.

---

## The idea

The basic idea is:

**rail vibrates → accelerometer records it → ESP32 processes the data → compare the vibration with known tight/loose cases**

The motor in my setup is standing in for the vibration produced by a passing train. The point of the bench experiment is to find out whether the joint actually produces a measurable difference when the bolts are loosened.

If the difference is consistent enough, the same idea could eventually be tested on a moving vehicle.

For now, this is a **bench-scale experiment**, not a railway safety system.

---

## What I built

I fabricated a small steel track section with a real bolted fishplate joint and built the electronics around it.

### Hardware

- ESP32-S3 Zero
- MPU-6050/6500 accelerometer board
- MicroSD module
- Motor used as a repeatable vibration source
- L298N motor driver
- HX711 amplifier + load cell for bolt-force measurements
- Fabricated steel track and fishplates
- Plywood base
- Perfboard electronics

### Software

- Arduino C++ firmware
- Accelerometer sampling at up to 1 kHz
- SD-card data logging
- FFT/frequency analysis
- Python serial data logging and analysis

---

## The project did not go exactly as planned

My first idea was to detect a loose bolt by looking for a change in the rail's natural frequency.

I did the calculation first.

Depending on how the rail is supported, the calculated frequencies came out roughly between **470 Hz and 17 kHz**.

Then I checked the accelerometer.

It samples at about **1 kHz**, so because of the Nyquist limit I can only reliably measure frequencies up to about **500 Hz**.

So most of the thing I was planning to measure was outside the sensor's useful range.

That changed the experiment. Instead of trying to measure the rail's full natural-frequency response, I started looking at how the **joint itself moves and vibrates** when the bolts are loose.

Then I found another problem.

The plywood board holding the track was moving slightly when the motor ran. That meant the accelerometer was measuring some movement from the whole rig, not just the joint.

I clamped the board down and started a new set of measurements.

The old data is still in `code/Inaccurate Readings/`. I kept it because it is part of the development of the experiment, not because it should be used for the final result.

---

## What the data says so far

The first clamped-board dataset is encouraging, but it is not the final answer.

The average vibration changes noticeably as the bolt state changes. The difference between the more loose states and the more secure states is fairly clear.

The harder case is distinguishing **3 bolts tight from 4 bolts tight**. That difference is currently small enough that normal run-to-run variation can overlap with it.

So I am not calling a final threshold yet.

There is also a timing/recording issue in one of the runs where not all three accelerometer axes were recorded for the full capture. That needs to be fixed before I rely on the next round of data.

---

## Where the project stands

### Done

- Project idea and research direction
- Bill of Materials
- Main track and fishplate design
- Track manufacturing
- Main electronics assembly
- ESP32-S3 setup
- Accelerometer testing
- SD-card logging
- Initial vibration data collection
- FFT/frequency analysis
- Natural-frequency calculation
- Identification of the actual MPU-6500 chip
- Identification and correction of the board-movement problem
- First controlled clamped-board dataset

### Still being worked on

- Fixing and checking the remaining timing/recording issue
- Building a larger clean dataset
- Finding a reliable tight/loose threshold
- Repeated testing of the classification
- Completing the circuit box
- Completing/testing the motor + L298N setup
- Testing the HX711 + load cell
- Adding automatic vibration detection
- Starting the frequency calculation automatically when vibration is detected
- Building the laptop UI with a frequency graph and tight/loose output
- Adding the final red/green tight/loose indication

---

## Why I'm interested in it

Railway inspection already exists, so I am not trying to replace the systems that are already used on real railways.

What interested me was a different question:

**What if a train could collect some information about the track while it was already travelling normally?**

A small sensor would not replace a proper inspection. But if it could flag a joint that looks unusual, it could give an engineer another reason to take a closer look.

Right now, I'm trying to get one small steel joint on a table to give me a result I can actually trust.

That's hard enough.

---

## Explore the project

The repository contains the build, calculations, code, data, mistakes, photos and project logbook.

- [`analysis/`](analysis/) — data collection and analysis
- [`code/`](code/) — ESP32 tests, data collection and experimental readings
- [`docs/`](docs/) — design, build, electronics, software, theory and problems
- [`hardware/`](hardware/) — schematics, drawings, BOM and 3D model
- [`logbook/`](logbook/) — handwritten project logbook
- [`media/`](media/) — photos and videos
- [`presentations/`](presentations/) — project presentation
- [`specification_sheets/`](specification_sheets/) — component datasheets

If you want to see the technical side, start with [`docs/`](docs/).

If you want to see what went wrong, read [`docs/PROBLEMS.md`](docs/PROBLEMS.md).

If you want to see the data, go to [`code/Accurate Readings/`](code/Accurate%20Readings/).

---

### The question I'm still trying to answer

**Can a cheap accelerometer tell me that a railway joint is getting loose before the problem becomes obvious?**
