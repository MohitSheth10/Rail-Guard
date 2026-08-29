# Code

This folder contains the firmware tests, data-collection tools and experimental data used during Rail-Guard.

The code developed in this project is not one finished program yet. Different folders and scripts came from different stages of testing.

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

This folder contains the newer controlled data and is the dataset to use for the current experiment.

### `Inaccurate Readings/`

Earlier experimental data collected before the board-movement problem was found and fixed.

These files are intentionally kept.

They are useful because they show what the experiment looked like before the mechanical problem was discovered, but they should not be used as the main dataset for the final tight-vs-loose conclusion.

### `ML_Training_Scenarios.txt`

This file contains the planned scenarios for future classification/ML work.

It should not be interpreted as evidence that a trained machine-learning model has already been completed.

---

## Current coding work

The next software work is focused on turning the data collection into an actual detection system:

- collect a larger clean dataset
- fix the remaining timing/axis recording issue
- compare the tight and loose states
- determine a reliable threshold
- automatically detect when vibration starts
- start the frequency calculation automatically
- send the final result to the laptop UI
- eventually output a clear tight/loose state
