# Rail-Guard

**Finding loose railway bolts by listening to how the track shakes.**

---

## Why I chose this

Rails come in fixed lengths. Where two lengths meet, they're joined by a **fishplate** -- a steel bar bolted across both rail ends, usually with four bolts, holding the joint in line so a wheel can cross it without dropping.

Those bolts loosen over time. Trains pass, the joint flexes, and eventually a bolt backs off. A loose joint lets the two rail ends move independently, and joint failure is a known contributor to derailments. It's also slow to develop -- there's a real window where the problem exists before it becomes visible.

Right now it's mostly found by eye or by hammer-tap: someone walks the section and checks it by hand. That works, but it's slow, and a given joint only gets checked every so often.

**The idea:** put an accelerometer on the joint, use a motor to create repeatable vibration standing in for a passing train, and find out whether a tight joint and a loose joint actually vibrate differently enough to tell apart automatically.

This is a bench-scale prototype, not a deployed railway system.

---

## What I built

A fabricated track section with one real bolted fishplate joint (steel T-section rails with a welded head plate), mounted on a plywood base, with a motor-driven mechanism standing in for a passing train.

**Hardware:** ESP32-S3 Zero, MPU-6050/6500 accelerometer, HX711 amplifier + load cell (for future bolt-force sensing), microSD module, L298N motor driver -- soldered onto perfboard since vibration and loose jumper wires don't mix.

**Software:** Arduino C++ firmware sampling the accelerometer at up to 1 kHz, a Python serial logger, and Python analysis tools that run an FFT on each capture and call the joint TIGHT or LOOSE.

---

## The steps, the problems, and how the plan changed

The full account is in [docs/PROBLEMS.md](docs/PROBLEMS.md); this is the short version.

**The rail steel didn't exist off the shelf.** Model railway track is moulded plastic; structural I-beams aren't shaped like a rail. I had 2-inch steel T-sections cut and a flat plate welded along the top to form the rail head -- which made the section asymmetric and meant working out the true centroid by hand before any beam calculation meant anything (worked through in [docs/06-theory.md](docs/06-theory.md)).

**The original plan couldn't work.** The first idea was to detect a loose bolt from a shift in the rail's own natural frequency. That calculation came out somewhere between roughly 470 Hz and 17 kHz depending on how the rail is supported -- and the accelerometer, sampling at about 1 kHz, can only trust readings up to about 500 Hz (Nyquist's limit). Most of what I'd planned to measure was outside what the sensor could actually see. So the target changed: not the rail's own ringing frequency, but how the *joint* itself moves when bolts are loose.

**The sensor wasn't quite what the board claimed.** Reading the accelerometer's WHO_AM_I register returned `0x70`, not the `0x68` a true MPU-6050 should return -- the board is actually an MPU-6500, sold under the MPU-6050 name on the same GY-521 module. Mostly compatible, except the low-pass filter lives in a different register on each chip, so the firmware now checks the chip's identity at startup instead of assuming.

**A quieter problem: the whole board was moving.** Early readings looked plausible on their own but didn't add up to a clean tight-vs-loose story between runs. The plywood board itself was shifting slightly under its own vibration, so part of what the sensor picked up was the rig moving, not the joint. Fixed on **29 August** by clamping the board down. Every reading collected before that is kept in [code/Inaccurate Readings](code/Inaccurate%20Readings) for reference, not for conclusions; everything after goes into [code/Accurate Readings](code/Accurate%20Readings).

**Finding a number that actually separates tight from loose.** The obvious candidates didn't hold up on their own: overall vibration loudness (RMS) can't tell a missing fishplate apart from a properly tightened joint -- their RMS ranges overlap. Picking "whichever single frequency is loudest" isn't reliable either, since most readings contain two frequencies close in strength (roughly 39 Hz and its ~79 Hz echo), and which one narrowly wins can flip between otherwise-identical readings. What held up: the *ratio* of vibration energy in the 30-60 Hz band to the 60-100 Hz band. Checked against every reading collected so far (0-4 bolts tight, the fishplate removed entirely, and stationary baselines), every 3-4-bolt reading scored below 0.30 and every not-secure reading scored above 0.38 -- a clean gap, with the working threshold set at 0.35. See [analysis/README.md](analysis/README.md) for the full reasoning.

---

## Where the project stands

| Part | Status |
|---|---|
| ESP32-S3 controller | Tested |
| MicroSD logging | Tested |
| MPU accelerometer | Tested, sampling verified |
| Motor + L298N driver | Vibration confirmed; formal module test still pending |
| HX711 + load cell | Soldered, not yet tested |
| Natural-frequency calculation | Done -- the result that redirected the whole approach |
| Board-drift systematic error | Found and fixed (29 Aug) |
| Controlled dataset | Collected: 0-4 bolts tight, no-fishplate, stationary baselines, 3 reps each |
| FFT + tight/loose analysis | Built and checked against the full dataset -- see `analysis/` |
| Fine-grained bolt count (1 vs 2 vs 3) | Not yet reliable -- only 3 reps per state so far |
| Live/real-time detection | Not built yet -- current tools run on saved recordings |

---

## Everything, linked

- [docs/](docs/) -- concept, design, build, electronics, software, theory, and every problem hit along the way
- [analysis/](analysis/) -- the FFT tool and the tight/loose classifier, and how they work
- [code/](code/) -- firmware tests, the data logger, and the experimental readings
- [hardware/](hardware/) -- schematic, wiring, bill of materials, 3D model
- [logbook/](logbook/) -- dated project logbook
- [media/](media/) -- photos and video of the build
- [presentations/](presentations/) -- project pitch deck
- [specification_sheets/](specification_sheets/) -- component datasheets

---

## What's next

1. Collect more repeats per bolt state to test whether 1/2/3-bolt states can be told apart reliably, not just "secure vs. not"
2. Decide whether live detection runs on a laptop watching the sensor stream, or gets built into the ESP32 firmware directly
3. Test the HX711 + load cell and calibrate against known weights
4. A clear tight/loose readout (LED or similar) once the detection logic is trusted

---

## Built with

ESP32-S3 · MPU-6050/6500 accelerometer · HX711 + load cell · L298N motor driver · Arduino C++ · Python · mild steel, plywood, and a local welding shop
