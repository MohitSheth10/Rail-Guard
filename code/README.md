# Code

This folder contains the firmware, data-collection tools and experimental data used during Rail-Guard.

The code runs as a set of focused scripts rather than one monolithic program — firmware sketches, a data logger, and the analysis/classification tools — each covering one stage of the pipeline described in the [root README](../README.md).

## Folders and files

### `MPU_Test/`

Basic accelerometer bring-up and testing code.

This was used to check that the accelerometer could communicate with the ESP32 and return usable readings.

### `SD_Card_Test/`

Code used to test SD-card read/write operation.

The SD card is used to store experiment data rather than relying only on the Serial Monitor.

### `daq.py`

Python serial logger used to record the ESP32's output into CSV files.

This is the version actually used to record the datasets in `Accurate Readings/` and `Inaccurate Readings/`. It reads the ESP32's own timestamps and watches for stalled or off-rate sampling while it records, which the earlier logger in [`analysis/daq.py`](../analysis/daq.py) doesn't do — that one is kept because the analysis workflow described in [`analysis/README.md`](../analysis/README.md) still references it.

The logger makes it possible to save a complete experiment and analyse it afterwards.

The main analysis tools are in [`../analysis/`](../analysis/).

### `Accurate Readings/`

Data collected after the plywood base was clamped down.

The earlier test setup allowed the board itself to move during vibration, so the old readings could contain movement from the whole rig.

This folder contains the controlled data used for the project's results.

Each file is named `capture_<bolts>vibrating<reading>.csv` — so `capture_0vibrating1.csv` is the 1st reading with 0 of 4 bolts tightened, and `capture_4vibrating3.csv` is the 3rd reading with all 4 bolts tightened. `capture_nofishplate*.csv` are readings with the fishplate removed entirely, and `capture_stationary*.csv` are baseline readings with the motor off. (`capture_stationary2.csv` was removed — it was recorded in an older logging format and isn't compatible with the current analysis scripts.)

The FFT and tight/loose analysis built on this data lives in [`../analysis/`](../analysis/) — `fft_analysis.py` turns a capture into a frequency breakdown, and `classify_tightness.py` uses that to call each reading TIGHT or LOOSE. Checked against every reading here, a ratio threshold of 0.35 cleanly separates the two: every 3-4 bolt reading scores below 0.30, and every not-secure reading (0-2 bolts, or no fishplate) scores above 0.38. See [`analysis/README.md`](../analysis/README.md) for the full reasoning.

### `Inaccurate Readings/`

Earlier experimental data collected before the board-movement problem was found and fixed.

These files are kept for reference and transparency — several are visibly corrupted or empty, documenting the bug rather than hiding it — but they aren't used for the final tight-vs-loose conclusion.

---

## How the pieces fit together

`daq.py` logs a capture, `fft_analysis.py` turns it into frequency content, `classify_tightness.py` applies the tuned 0.35 threshold, and [`analysis/liveclassifytightness.py`](../analysis/liveclassifytightness.py) runs that same logic live against the ESP32's real-time stream instead of a saved file. See the [root README](../README.md) for the full step-by-step and the results.
