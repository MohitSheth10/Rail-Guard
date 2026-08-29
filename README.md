# Rail-Guard

**Finding loose railway bolts by listening to how the track shakes.**

IBDP Extended Project — Mohit Sheth

---

## Ideation

Rails come in fixed lengths. Where two lengths meet, they're joined by a **fishplate** — a steel bar bolted across both rail ends, usually with four to six bolts, holding the joint in line so a wheel can cross it without dropping.

Those bolts loosen. Trains pass, the joint flexes, temperature swings the rail back and forth, and over enough cycles the nuts back off. A loose joint lets the two rail ends move independently, and joint failure is a known contributor to derailments. It's also slow to develop — a bolt doesn't loosen overnight, which means there's a real window where the problem exists and could be caught.

Right now it's mostly found by eye: someone walks the section and looks, or a track-recording vehicle measures geometry and catches the consequences of a bad joint rather than the joint itself. Both work. Both are expensive per kilometre, and both mean a given joint gets checked every few weeks at best.

**The idea:** put an accelerometer on something already travelling the line and let it listen. A wheel crossing a tight joint and a wheel crossing a loose one don't shake the same way — the loose one has more movement in it, the rail ends shift against each other, and the impact is sharper and less damped. If a sensor can reliably tell those two apart, every passing train becomes an inspection, instead of one every few weeks.

To be honest about what's new here: vibration-based looseness detection is an active research area in structural engineering, and dedicated rail inspection vehicles already exist commercially. What's different about Rail-Guard is the angle — a cheap sensor, aimed specifically at the fishplate joint, cheap enough to put on ordinary rolling stock rather than a dedicated inspection vehicle.

The scope for this build is a working bench model, not a product: a fabricated track with one real bolted fishplate joint, a motor standing in for a passing train, an accelerometer reading the vibration, and an ESP32-S3 sampling it and eventually deciding loose or tight on its own.

---

## The steps, the problems, and how the plan changed

This is the honest, in-order version of how the project actually went — including the parts that didn't work the first time, and the parts I only just fixed. A full entry-by-entry list lives in docs/PROBLEMS.md; this is the shorter version, and it's still being added to as the project goes.

**Nobody sells the rail I needed.** Model railway track is moulded plastic with the rail shape only suggested. Structural steel suppliers sell I-beams, but not at this scale and not shaped like a rail. I ended up buying 2-inch steel T-sections from a local shop and having a flat plate welded along the top of each to form a rail head — the base and web from the T, the head from the weld.

**That shortcut had a cost I didn't see coming.** The welded plate is narrower than the base of the T, so the finished rail is asymmetric top to bottom. Every textbook beam formula assumes the top and bottom flanges match. Mine don't, so before I could calculate anything I had to find the true centroid and apply the parallel axis theorem by hand. More work than the shortcut looked like it would save — worked through step by step in docs/06-theory.md.

**The sensor physically could not hear what I was originally trying to measure.** The first plan was to calculate the rail's natural frequency — the pitch it rings at — and watch that pitch shift when a bolt loosened. The calculation came out somewhere between 470 Hz and 17 kHz depending on how the rail is supported. Then I checked the sensor: the accelerometer updates at 1000 Hz maximum, which puts the highest frequency it can trust at about 500 Hz by Nyquist's limit. It cannot hear the rail ring — and worse, it wouldn't have failed obviously. Frequencies above that ceiling fold back down and show up as convincing low frequencies that aren't real. If I hadn't checked, I'd have built the whole detection system on a number that was an artifact and it would have looked like it was working. So the target changed: a loose bolt doesn't change the stiffness of the steel, it changes how the joint moves — the two rail ends shifting against each other, which is a heavier, floppier system that sits comfortably inside what the sensor can actually measure.

**The sensor wasn't the sensor the board said it was.** Reading the WHO_AM_I register returned 0x70, not the 0x68 an MPU-6050 should give. The chip on the board is actually an MPU-6500, sold on the same GY-521 board under the MPU-6050 name. Mostly compatible, except the accelerometer's low-pass filter lives in a different register on each chip — so the firmware now reads the chip's identity at startup and configures the correct register instead of assuming.

**Getting from a slow test read to a trustworthy fast one took four separate fixes.** The first working sketch printed a reading twice a second — fine for proving the sensor is alive, useless for vibration. Reaching a real, provable 1000 Hz meant raising the I2C bus speed, correctly configuring the sensor's own internal sample-rate registers, replacing delay() with absolute-deadline timing so errors don't pile up over a capture, and no longer printing to Serial during a capture, since that alone was silently slowing the whole loop down while the data still looked fine.

**Once I had real capture data, a quieter problem showed up: the board itself was moving.** The first full round of stationary/vibrating/loose readings looked believable at a glance, but comparing runs turned up inconsistencies that didn't match a clean tight-vs-loose story — swings that tracked when a reading was taken more than what state the bolts were in. The cause turned out to be simple and a little embarrassing: the wooden board the track sits on could shift position slightly under its own vibration, so part of what the sensor was picking up was the whole rig creeping around, not just the joint. That's a systematic error, not noise — it doesn't average out, it just quietly biases every reading depending on how the board happened to have drifted that day.

**The fix, as of August 29th: two clamps.** The board is now physically clamped down so it can't creep during a run. Every reading in code/Inaccurate Readings predates this fix, which is exactly why that folder is named what it is — not wrong data, just data collected before I understood and controlled for this source of error. Everything from here on goes into code/Accurate Readings instead. The new protocol is deliberately more methodical than the first pass: three one-minute baseline readings with the motor off, then one-minute readings with the motor vibrating at each bolt state in turn — all four bolts tight, then one loosened, two loosened, three loosened, and finally all four loose — several readings at each state rather than one. The goal is a data set clean enough to actually trust the tight-vs-loose comparison, instead of one where board drift could be hiding or faking the effect I'm looking for.

**Single sensor for now, on purpose.** The board has two accelerometers wired for the eventual two-point design, but for this prototype and testing phase only one is connected and tested at a time — simpler to debug, and the second sensor is electrically identical, so it's expected to behave the same once it's brought back in.

**First real result: the rig actually works.** With a serial logger (code/daq.py) built to save a run to CSV instead of just watching it scroll past, the first proper capture showed a flat, quiet signal while stationary and a clear, sustained jump in vibration the instant the motor started — proof the whole chain, sensor to board to logger, is picking up what it's supposed to. The clamped-board data now being collected is the step that finds out whether it can tell tight from loose.

---

## What's been done so far

**Physical build**
A 24-inch fabricated track with one real bolted fishplate joint (steel T-section rails with a welded head plate), a plywood base — now clamped down to remove board drift — and a motor-driven mechanism that stands in for a passing train.

**Electronics**
ESP32-S3 Zero as the main controller, an MPU-6050/6500 accelerometer as the primary sensor, an HX711 amplifier with a load cell for bolt clamping force (Phase 2), a microSD module for logging, and an L298N driver running the motor — all soldered onto perfboard rather than breadboarded, since vibration and loose jumper wires don't mix.

**Firmware**
An MPU bring-up test, an SD card read/write test, and the current working piece: an onboard FFT stage that samples the accelerometer at a fixed rate and reports the dominant vibration frequency live, instead of raw numbers.

**Data tooling and data**
A Python serial logger (daq.py) that records a run to CSV with a live readout while it's capturing, plus a small plotting script for reviewing a run afterwards. Older stationary/vibrating/loose-bolt runs, collected before the board was clamped, are kept in code/Inaccurate Readings for reference. The new, methodical clamped-board data set is being collected into code/Accurate Readings.

**Documentation**
A full written record of the project from concept through theory (docs/), the as-built schematic, wiring diagram, bill of materials and a 3D track model (hardware/), every component's datasheet (specification_sheets/), the handwritten logbook scanned in full (logbook/), and the project pitch deck (presentations/).

**Current status**

| Part | Status |
|---|---|
| ESP32-S3 controller | Tested — boots reliably, verified over USB |
| MicroSD logging | Tested — writes and reads back correctly |
| MPU accelerometer | Tested — sampling verified, live FFT working |
| Motor + L298N driver | Vibration confirmed in first capture run — formal module test still pending |
| HX711 + load cell | Soldered, not yet tested |
| Natural frequency calculation | Done — the result that redirected the whole detection approach |
| Board-drift systematic error | Found and fixed (Aug 29) — rig is now clamped down |
| Loose-vs-tight threshold | Not yet answered — clamped-board data collection in progress |

---

## Everything, linked

The write-up above is the short version. Here's where the actual work lives.

**The story, in full**

| | |
|---|---|
| docs/01-concept.md | The problem, how it's found today, what already exists |
| docs/02-design.md | Dimensions, rail section, fishplate, sensor mounting |
| docs/03-build.md | Fabricating the rails, fishplates, base, cart |
| docs/04-electronics.md | Components, wiring, pin map, assembly |
| docs/05-software.md | Firmware, the 1 kHz capture sketch, what's next |
| docs/06-theory.md | Natural frequency of the rail section, worked step by step |
| docs/PROBLEMS.md | Every problem hit, in order — the most useful file in the repo |
| logbook/Project_LogBook.pdf | The handwritten logbook, scanned in full |

**The code**

| | |
|---|---|
| code/MPU_Test | Accelerometer bring-up sketch |
| code/SD_Card_Test | SD card read/write test |
| code/daq.py | The serial data logger — records a live run to CSV |
| analysis/natural_frequency.py | The beam and frequency calculation, from measured dimensions |

**The data**

| | |
|---|---|
| code/Accurate Readings | The clamped-board data set — the one to trust, being built up run by run |
| code/Inaccurate Readings | Earlier runs, collected before the board-drift fix — kept for reference, not for conclusions |

**The hardware**

| | |
|---|---|
| hardware/schematic | As-built schematic and circuit photos |
| hardware/wiring.drawio | Editable wiring diagram |
| hardware/bill_of_materials.xlsx | Full parts list |
| hardware/track_drawings.pdf | Track and joint drawings |
| hardware/track_3d_model.html | 3D model of the track |
| specification_sheets | Datasheets for every component used |

**Everything else**

| | |
|---|---|
| presentations | The project pitch deck |
| media | Photos and video of the build and testing |

---

## What's next

1. Collect the full clamped-board data set: three stationary baselines, then several one-minute runs at each bolt state — tight, one loose, two loose, three loose, four loose
2. Compare those runs and see whether tight and loose are actually separable
3. Pick a threshold and see how often it gets the call right
4. Test the HX711 and load cell, and calibrate against known weights
5. If it works, an LED or similar indicator for a live tight/loose readout

6. Page_Down

7. ---

8. ## Built with

9. ESP32-S3 · MPU-6050/6500 accelerometer · HX711 + load cell · L298N motor driver · Arduino C++ · Python · mild steel, plywood, and a local welding shop
10. 
