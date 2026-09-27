# Rail-Guard

**Finding loose railway bolts by listening to how the track shakes.**

A bench-scale prototype that puts an accelerometer on a bolted rail joint, shakes the joint with a motor standing in for a passing train, and decides — automatically, from the vibration signal alone — whether the joint is securely bolted or not.

---

## Problem Statement

Rails come in fixed lengths. Where two lengths meet, they're joined by a **fishplate** — a steel bar bolted across both rail ends, usually with four bolts, holding the joint in line so a wheel can cross it without dropping.

Those bolts loosen over time. Trains pass, the joint flexes, temperature swings the rail back and forth, and eventually a bolt backs off. A loose fishplate joint lets the two rail ends move independently: the gap opens, the alignment goes, and the joint starts hammering itself apart under every wheel that crosses it.

This isn't a minor maintenance detail. The U.S. Federal Railroad Administration tracks "rail defects at bolted joint" and "joint bar defects" as their own distinct derailment-cause categories, separate from general track geometry problems — and in the most detailed peer-reviewed analysis of U.S. Class I mainline derailment causes (Wang et al., 2020, *ASCE Journal of Transportation Engineering*, using 2006–2015 FRA accident data), broken rails and welds — the same family of joint and rail-continuity failures — were the single most frequent cause of mainline freight derailments over the entire ten-year study period. Joint problems are also slow to develop: a bolt doesn't back off overnight, which means there is a real window, often weeks or months long, where the fault exists and could be caught before it causes a derailment.

Right now, that window is mostly wasted. Joints are checked by eye or by hammer-tap: someone walks the section and inspects it by hand, or a dedicated track-recording vehicle runs the line every so often. Both work, but both are expensive per kilometer of track, and neither watches a joint continuously — a given joint gets looked at every few weeks at best.

**What loosening actually looks like** — the short video below shows the joint on this rig running under motor-driven vibration with the fishplate bolts progressively backed off. Watch how the joint's own movement changes as the bolts loosen: [`media/videos/bolt-loosening-vibration-demo.mp4`](media/videos/bolt-loosening-vibration-demo.mp4).

**The idea this project tests:** mount a cheap accelerometer directly on the joint, and find out whether a tight joint and a loose joint vibrate differently enough — under repeatable, motor-driven vibration standing in for a passing train — to be told apart automatically, in real time, by a microcontroller alone.

---

## Research Question and Hypothesis

**Research question:** Can the vibration signature of a bolted rail fishplate joint, captured by a low-cost MEMS accelerometer and analyzed in the frequency domain, reliably distinguish a securely tightened joint from one that is not — and can that distinction be made automatically, without a person inspecting the joint?

**Hypothesis:** When a bolted joint is shaken by a repeatable external vibration source, the *distribution* of vibration energy across frequency bands — specifically, the balance between a lower-frequency band and a higher-frequency band in the joint's response — will differ measurably and consistently between a securely tightened joint (3–4 of 4 bolts tight) and a joint that is not secure (0–2 bolts tight, or the fishplate removed entirely). A loose joint has more freedom to move, which damps the higher-frequency response and pushes relatively more energy into the lower-frequency band; a tight joint is more rigidly coupled and does the opposite.

---

## Engineering Goal

Build a working bench-scale system that:

1. Physically reproduces a real bolted fishplate joint under controlled, repeatable vibration (a motor-driven mechanism standing in for a passing train), rather than relying on simulation alone.
2. Samples the joint's vibration fast enough, and cleanly enough, to resolve the frequency content that actually matters — not just "how hard is it shaking."
3. Finds a single, well-separated numerical threshold that calls a joint TIGHT or LOOSE from that vibration data, validated against a real, controlled dataset covering every bolt count from 0 to 4, plus a no-fishplate and a stationary baseline.
4. Runs that same classification live, on the actual serial stream from the sensor, with a real-time TIGHT/LOOSE readout — not just after the fact on a saved recording.

This is a bench-scale prototype, not a deployed railway system — the goal is to prove the detection principle works, not to ship hardware for a real track.

---

## Methodology

### 1. Building a real joint to test on

A fabricated track section was built with one real bolted fishplate joint, rather than simulating one, because a simulated joint can't show whether real hardware, real bolt threads, and real vibration actually behave the way the theory predicts.

Model railway track is moulded plastic and structural I-beams aren't shaped like a rail, so the rail sections were fabricated from 2-inch mild-steel T-section with a flat plate welded along the top to form the rail head — full dimensions and the welding decision are in [`hardware/`](hardware/). This made the rail's cross-section **asymmetric** (the welded top plate is narrower than the base), which turned out to matter a lot for the physics in step 2.

The joint sits on a plywood base, with a motor-and-cart mechanism ([`hardware/schematic/`](hardware/schematic/), wiring diagram in [`hardware/wiring.drawio`](hardware/wiring.drawio)) providing repeatable, controlled vibration standing in for a passing train, so the same "event" could be reproduced across every bolt-count test. The full parts list — what was actually wired into the final build, quantities corrected down from everything that was purchased along the way — is [`hardware/RailGuard_BOM_AsBuilt.xlsx`](hardware/RailGuard_BOM_AsBuilt.xlsx); component datasheets are in [`specification_sheets/`](specification_sheets/).

**Electronics:** an ESP32-S3 Zero as the controller, an MPU-6050/6500 accelerometer reading the joint's vibration, an HX711 amplifier and load cell (for future bolt-force sensing), a microSD module, and an L298N motor driver for the vibration source — soldered onto perfboard rather than left on breadboard jumpers, because loose jumper wires and a vibration rig do not mix.

### 2. The physics first — why the original plan didn't work

Before writing any detection code, the natural question was: what frequency does this rail section actually resonate at, and can the sensor even see it? Getting this wrong first saved a lot of wasted effort later, so it's worth walking through.

The rail's cross-section is asymmetric (narrower welded top flange, wider base), so the standard symmetric I-beam formula doesn't apply — the neutral axis (the line the section bends around) isn't at mid-height. Splitting the section into three rectangles and finding the area-weighted centroid puts it at **21.4 mm above the bottom**, about 7 mm lower than the section's geometric mid-height of 28.4 mm. From there, the second moment of area (using the parallel-axis theorem, since each rectangle sits a different distance from the true centroid) comes out to **I = 166,448 mm⁴**. The full worked calculation, piece by piece, is in [`analysis/natural_frequency.py`](analysis/natural_frequency.py) (script) and [`docs/06-theory.md`](docs/06-theory.md) (write-up).

Feeding that into the standard beam natural-frequency formula —

```
        λ²        ┌───────────
f  =  ────── ×  \╱   EI / (m·L⁴)
       2π
```

— for mild steel (E = 200 GPa, ρ = 7,850 kg/m³) across the spans and end conditions relevant to this rig gives a fundamental natural frequency **somewhere between roughly 168 Hz (the whole 609.6 mm track, cantilevered) and about 38 kHz (a single 101.6 mm sleeper-to-sleeper span, clamped at both ends)** — with the most physically realistic case, the whole track simply supported, landing around 470 Hz.

That range mattered because the MPU's accelerometer samples at **1,000 Hz maximum**. By the Nyquist limit, that means it can only resolve frequencies up to about 500 Hz, and realistically less. Almost every case in that frequency table — everything except the very lowest-span, most flexible mounting — sits above what the sensor can actually see. Pointing an FFT at the rail's own ringing frequency would have meant either seeing nothing real, or worse, seeing *aliasing*: a plausible-looking low frequency that doesn't correspond to anything physically real.

**This is the finding that changed the whole approach.** Rather than trying to detect a loose bolt from a shift in the *rail's own* resonant frequency, the target became the **joint** itself — the fishplate, bolts, and base moving together as a much heavier, much lower-frequency system. A loose bolt doesn't change the stiffness of the steel rail; it changes how the two rail ends move against each other, and that's a low-frequency signal well within what a 1 kHz accelerometer can resolve. Every FFT and classification step below is built on that redirected target, not the original one.

### 3. The code, step by step

The firmware and analysis tools were built incrementally, each one solving the specific problem the previous one exposed, ending at the live tool this project currently runs. In order:

**Step 1 — prove the sensor is even there.** [`code/MPU_Test/MPU_Test.ino`](code/MPU_Test/MPU_Test.ino) is the first sketch: wake the MPU over I2C and print raw X/Y/Z accelerometer counts once every half-second. It originally wired the sensor to GPIO 6/7. This step's only job was answering "is this chip actually talking to the board" — and it also surfaced the first real hardware problem: reading the sensor's WHO_AM_I identification register returned `0x70`, not the `0x68` a true MPU-6050 should report. The board was actually an **MPU-6500**, sold under the MPU-6050 name on the same GY-521 module — mostly register-compatible, but with its low-pass filter configuration living in a different register, so every sketch after this one checks the chip's real identity at startup instead of assuming.

**Step 2 — sample fast enough, and check what "fast enough" even means.** Basic `delay(500)`-based reads are nowhere near fast enough to catch vibration in the 30–100 Hz range this project targets (step 2 above explains why that range, not a higher one, is the right target). [`code/mpu6050_1khz_stream/mpu6050_1khz_stream.ino`](code/mpu6050_1khz_stream/mpu6050_1khz_stream.ino) is the sketch this project actually runs: it moves the sensor to its final wiring (SDA=GPIO8, SCL=GPIO9), configures the correct accelerometer registers for the MPU-6500 (±8g full-scale range, widest available filter bandwidth, 1000 Hz output rate — the accelerometer's hardware maximum), and uses an absolute-deadline scheduler (no `delay()` anywhere in the sample loop) to keep every sample within microseconds of its ideal 1 ms interval. It streams one line per sample — `sample_index,micros,ax,ay,az` — over serial, continuously, for as long as a PC logger is listening.

**Step 3 — get that stream onto a computer.** [`analysis/daq.py`](analysis/daq.py) is the PC-side logger: it opens the serial port at 115200 baud, reads the stream, and writes every row to a timestamped CSV, auto-detecting whether one or two sensors are streaming from the column count. It also averages the first 100 samples as a per-axis zero point and subtracts it from everything after, so the raw counts in the CSV are already roughly centered around zero instead of sitting on top of whatever gravity offset the sensor happens to be mounted at.

**Step 4 — turn raw numbers into frequency content.** [`analysis/fft_analysis.py`](analysis/fft_analysis.py) loads a capture, automatically trims it to just the vibrating segment (so a quiet lead-in before the motor starts doesn't water down the result), and runs a windowed FFT on the combined X/Y/Z magnitude signal. It reports the dominant frequency, the overall vibration RMS, and — critically for the next step — the energy split across a set of frequency bands.

**Step 5 — find the number that actually separates tight from loose.** This is the core analytical result of the project, detailed fully in section 4 below and in [`analysis/README.md`](analysis/README.md). [`analysis/classify_tightness.py`](analysis/classify_tightness.py) takes the band-energy numbers from step 4 and applies a single tuned threshold to call a reading TIGHT or LOOSE, plus an experimental finer-grained bolt-count estimate.

**Step 6 — check that the separation is real, not luck.** [`analysis/statistical_analysis.py`](analysis/statistical_analysis.py) runs the classifier's core ratio across every 0–4 bolt reading collected, and tests the result with a one-way ANOVA and a Kruskal-Wallis test (which doesn't assume normally-distributed data — a better fit given only 3 repeats per bolt count), plus pairwise Mann-Whitney U tests between each adjacent bolt count. It's upfront about what n=3 per group can and can't prove statistically — see the Observation section below.

**Step 7 — make it live.** [`analysis/liveclassifytightness.py`](analysis/liveclassifytightness.py) is the current, final tool: instead of reading a finished CSV, it connects directly to the ESP32's serial stream, keeps a rolling 2-second window of the most recent samples, and re-runs the exact same tuned FFT and classification logic from steps 4–5 twice a second, live, in a small on-screen GUI with a big colored TIGHT/LOOSE readout, the bolt-count estimate, and the underlying numbers. It imports its constants directly from `fft_analysis.py` and `classify_tightness.py` rather than duplicating any tuned values, so re-tuning the threshold in one place updates the live tool automatically.

(A parallel, independent track tested a microSD logging path — [`code/SD_Card_Test/SDCardReaderTest.ino`](code/SD_Card_Test/SDCardReaderTest.ino) — for onboard data storage without a PC tether; it's tested and working but not yet wired into the main detection pipeline above.)

### 4. The differentiator: a frequency-band ratio, not raw loudness

The most important methodological decision in this project was *what number* to pull out of the FFT and threshold on. Three candidates were tried, checked against the full "Accurate Readings" dataset ([`code/Accurate Readings/`](code/Accurate%20Readings/)), and two of them failed:

- **Overall vibration loudness (RMS) alone is not reliable.** A completely missing fishplate can read about as quiet as a properly tightened joint — using RMS by itself risks missing the worst-case failure entirely.
- **"Which single frequency is loudest" is not reliable either.** Most readings contain two frequencies close in strength — roughly a slow ~39 Hz beat and a faster ~79 Hz echo of it — and which one comes out marginally louder can flip between two otherwise-identical readings at the same bolt count.
- **What does hold up: the ratio between two frequency bandwidths.** Specifically, the ratio of vibration energy in the 30–60 Hz band to energy in the 60–100 Hz band:

```
ratio = (energy in 30-60 Hz band) / (energy in 60-100 Hz band)
```

A securely tightened joint is more rigidly coupled and puts most of its shake into the faster ~79 Hz echo, so this ratio comes out **low**. A joint that isn't properly secured — 0, 1, or 2 bolts tight, or no fishplate at all — has more freedom to move, damping the higher-frequency response and leaving relatively more energy sitting in the slower ~39 Hz band, so the ratio comes out **high**. This bandwidth ratio, not raw loudness and not a single peak frequency, is the actual differentiator this whole detection system is built on.

### 5. Finding and fixing a systematic error

Early readings, even after settling on the ratio approach, didn't add up to a clean story between runs. The cause turned out to be mechanical, not analytical: the plywood base itself was shifting slightly under its own vibration, so part of what the sensor picked up was the *whole rig* moving, not the joint. This was found and fixed on **29 August** by clamping the board down. Every reading collected before that fix is kept in [`code/Inaccurate Readings/`](code/Inaccurate%20Readings/) for reference and transparency, not for conclusions — several of those files are visibly corrupted or empty, documenting the bug rather than hiding it. Every reading used in the actual analysis and results below comes from [`code/Accurate Readings/`](code/Accurate%20Readings/), collected after the fix.

---

## Observation

With the board-drift bug fixed, a controlled dataset was collected: **0, 1, 2, 3, and 4 bolts tight, plus a no-fishplate condition and a stationary (motor-off) baseline, 3 repeats each.**

Running the 30–60 Hz / 60–100 Hz ratio (Section 4 above) across every reading in that dataset:

- **Every 3–4 bolt (secure) reading scored below 0.30.**
- **Every not-secure reading (0–2 bolts, or no fishplate) scored above 0.38.**
- That's a clean, unambiguous gap with room to spare on both sides — the working TIGHT/LOOSE threshold was set at **0.35**, right in the middle of it.
- Vibrating readings consistently scored **well above ~6,000 RMS**; a stationary, motor-off reading scored around **36 RMS** — three orders of magnitude apart, which is why a simple RMS floor (`MIN_RMS`) is enough to reliably flag "not enough vibration to judge" before attempting a TIGHT/LOOSE call at all.

The statistical check ([`analysis/statistical_analysis.py`](analysis/statistical_analysis.py)) confirms this separation is a real, group-level effect and not coincidence — but it's honest about the limits of only 3 repeats per bolt count. With n=3 per group, a pairwise Mann-Whitney U test mathematically cannot produce a p-value below 0.1, no matter how separated the groups actually are — there simply aren't enough possible orderings of 3-vs-3 data for anything stronger. That is a sample-size limit, not a failure of the detection method, and the overall pattern (group means ordered 0 > 1 > 2 > 3–4, with little to no overlap in ranges) is the more honest evidence.

Fine-grained bolt counting (telling 3 tight apart from 4 tight, specifically) is noticeably less reliable than the binary TIGHT/LOOSE call: the observed ratio ranges for 3-tight (0.285–0.298) and 4-tight (0.175–0.278) readings almost overlap, so [`analysis/classify_tightness.py`](analysis/classify_tightness.py) reports those two together as a combined "3–4 bolts tight" bucket rather than guessing which one it is — an honest read of what only 3 repeats per state can actually support.

---

## Results and Conclusion

The hypothesis holds, within the limits of this dataset: the ratio of vibration energy between the 30–60 Hz and 60–100 Hz bands reliably separates securely tightened rail-joint bolts from joints that are not secure, with a clean margin and a working threshold (0.35) that has correctly classified every reading collected to date, run both offline on saved captures and live on the real-time serial stream from the sensor ([`analysis/liveclassifytightness.py`](analysis/liveclassifytightness.py)).

**What's proven:** the core TIGHT/LOOSE distinction, live, on real hardware, across every bolt count from 0 to 4 plus a no-fishplate condition, with a clean statistical gap and a systematic mounting error found and fixed along the way rather than papered over.

**What's not yet proven:** reliable fine-grained bolt counting (distinguishing exactly how many of the 4 bolts are loose, rather than just "secure or not") — the 3-vs-4-tight boundary in particular needs more repeat readings before it can be trusted. The HX711 load-cell path for direct bolt-force sensing is soldered but not yet tested. And this remains a bench-scale prototype: a real deployed system would need to handle a moving train's own vibration as the excitation source instead of a fixed motor rig, validate against a wider range of joint hardware, and run a proper literature comparison against existing vibration-based bolt-looseness research (an open task — see [`docs/01-concept.md`](docs/01-concept.md)).

| Part | Status |
|---|---|
| ESP32-S3 controller | Tested |
| MicroSD logging | Tested |
| MPU accelerometer | Tested, sampling verified at 1 kHz |
| Motor + L298N driver | Vibration confirmed; formal module test still pending |
| HX711 + load cell | Soldered, not yet tested |
| Natural-frequency calculation | Done — the result that redirected the whole approach |
| Board-drift systematic error | Found and fixed (29 Aug) |
| Controlled dataset | Collected: 0–4 bolts tight, no-fishplate, stationary baselines, 3 reps each |
| FFT + tight/loose analysis | Built and statistically checked against the full dataset |
| Fine-grained bolt count (1 vs 2 vs 3 vs 4) | Not yet reliable — only 3 reps per state so far |
| Live/real-time detection | Built and working — [`analysis/liveclassifytightness.py`](analysis/liveclassifytightness.py) |

**Next steps:** collect more repeats per bolt state to test whether individual bolt counts (not just secure-vs-not) can be told apart reliably; test and calibrate the HX711 + load cell against known weights; add a simple physical TIGHT/LOOSE readout (LED or similar) once the live tool is trusted on more data; and run the literature comparison that would place this result against existing published work on vibration-based bolted-joint monitoring.

Further background, and the day-by-day account of problems hit along the way, is in [`docs/`](docs/) — [concept](docs/01-concept.md), [design](docs/02-design.md), [build](docs/03-build.md), [electronics](docs/04-electronics.md), [software](docs/05-software.md), [theory](docs/06-theory.md), and the full [problem log](docs/PROBLEMS.md). The dated project logbook is in [`logbook/`](logbook/), and the project pitch deck is in [`presentations/`](presentations/).

---

## Built with

ESP32-S3 · MPU-6050/6500 accelerometer · HX711 + load cell · L298N motor driver · Arduino C++ · Python (NumPy, pandas, SciPy) · mild steel, plywood, and a local welding shop

---

*Sources: FRA bolted-joint and joint-bar-defect derailment cause categories, and the 2006–2015 U.S. Class I mainline derailment-cause analysis, from Wang, Y., et al. (2020), "Quantitative Analysis of Changes in Freight Train Derailment Causes and Rates," ASCE Journal of Transportation Engineering, Part A: Systems, 146(11).*
