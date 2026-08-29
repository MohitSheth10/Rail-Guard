[← Back to main README](../README.md)

# Software

Firmware and data-capture code live in [`code/`](../code/). Analysis lives in
[`analysis/`](../analysis/).

---

## Where it is

Component bring-up is done. The accelerometer captures cleanly at a verified
1000 Hz, and a full clamped-board dataset across every bolt state has now been
collected (see the root [README](../README.md) and
[`code/Accurate Readings/`](../code/Accurate%20Readings/)). Turning that data into
a reliable, automatic tight/loose decision is the work still ahead.

## MPU bring-up sketch

[`code/MPU_Test/MPU_Test.ino`](../code/MPU_Test/MPU_Test.ino) — the original
bring-up sketch. Reads the accelerometer twice a second over the original GPIO 6/7
wiring and prints it. Useless for vibration analysis, but it's the right first
thing to run when checking whether a sensor is alive at all. Kept for that.

**Note on this file:** the actual 1000 Hz capture firmware — the sketch that
streams timestamped samples to the ESP32's serial port at close to 1000 Hz for
[`daq.py`](../code/daq.py) to log — is not currently checked into this repository,
only this earlier basic-test sketch is. That capture firmware exists on the device
Mohit builds with but hasn't been added here yet. Adding it is on the to-do list
below.

## SD card test

[`code/SD_Card_Test/SDCardReaderTest.ino`](../code/SD_Card_Test/SDCardReaderTest.ino)
— confirms the microSD module reads and writes before relying on it for logging.

## Data capture (Python side)

[`code/daq.py`](../code/daq.py) is the script actually used to record the datasets
in `code/Accurate Readings/` and `code/Inaccurate Readings/`. It reads the
ESP32's serial stream and saves it to a timestamped CSV, using the ESP32's own
`micros()` timestamps as the timing reference and watching for stalled or
off-rate sampling as it records. [`analysis/daq.py`](../analysis/daq.py) is an
earlier, simpler version of the same idea, kept because the `analysis/` workflow
still references it — see [`analysis/README.md`](../analysis/README.md) and
[`code/README.md`](../code/README.md) for how the two differ.

## Analysis

[`analysis/natural_frequency.py`](../analysis/natural_frequency.py) — section
properties and beam frequency from measured dimensions. Working explained in
[06-theory.md](06-theory.md).

---

## What's next

### Small tasks

- Add the actual 1000 Hz capture firmware sketch to the repo (see the note above)
- Verify the HX711 reads the load cell
- Calibrate the load cell against known weights
- Track down the timing/axis-recording glitch found in one of the 29 August
baseline files (see [PROBLEMS.md](PROBLEMS.md) and the logbook)

### Main tasks, in order

1. **Confirm the tight-vs-loose gap holds up.** The first clamped-board dataset
shows a clean, consistent drop in vibration as more bolts go in, with badly loose
(0–1 bolts) clearly separated from reasonably secure (3–4 bolts). The gap between
3 and 4 bolts is not yet reliably separated — it's smaller than the normal
run-to-run noise. More repeats are needed before trusting that split.

2. **Pick a threshold** that separates loose from tight, once the data supports one
with some confidence. No threshold has been chosen yet.

3. **Auto-trigger.** Detect the cart or motor run starting from the vibration
spike and use that to start the analysis automatically, rather than triggering by
hand.

4. **LED indicator.** On for loose, off for tight. Run the test repeatedly and
count how many it gets right.

### Then Phase 2

Load cell and HX711 — get a raw reading, calibrate, log force alongside
vibration, run both together.

Phases 3 (a trained ML model) and 4 (GPS) are out of scope for now. No machine
learning has been trained on this data yet — the current work is still about
whether simple vibration statistics (like RMS) can separate the bolt states at
all.

---

[← Electronics](04-electronics.md) · [Theory →](06-theory.md)
