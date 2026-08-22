[← Back to main README](../README.md)

# Analysis

## `daq.py`

Records the vibration stream from the ESP32-S3 over USB and saves it to a CSV file,
so a test run can be studied afterwards instead of just scrolling past on screen.

```bash
python daq.py
```

Needs `pyserial` (`pip install pyserial`). Set your board's COM port at the top of
the file first.

### What it does

- Reads roughly 1,000 lines a second from the board and writes every row to a
  timestamped CSV (`capture_YYYYMMDD_HHMMSS.csv`).
- Auto-detects the columns, so it works whether one or two accelerometers are streamed.
- Shows a live, once-a-second readout of the row count and rate while it records.
- Press `Ctrl+C` to stop; the file is flushed and closed cleanly, and it prints how
  many rows were saved and the true sample rate.

### First result

The first captured run showed a clear jump in the spread of the accelerometer values
the moment the motor started, against a flat, quiet baseline while it was stationary —
the first real sign that the rig picks up the vibration it's meant to measure.

## `natural_frequency.py`

Works out the section properties of the rail and its fundamental natural frequency
for a range of spans and end conditions.

```bash
python3 natural_frequency.py
```

No dependencies beyond the standard library.

### Using it

Measure the rail with a vernier caliper and edit the five numbers at the top:

```python
TOP_FLANGE_WIDTH = 21.0     # confirmed
BOT_FLANGE_WIDTH = 50.8     # confirmed
WEB_HEIGHT       = 50.8     # confirmed
FLANGE_THICKNESS = 3.0      # ASSUMED - measure this
WEB_THICKNESS    = 2.5      # ASSUMED - measure this
```

Two of those are still assumptions from the drawing, not measurements of the part.
Until they're checked, treat the output as an estimate.

### What it prints

- Area, centroid height, second moment of area
- Mass per metre and bending stiffness
- Fundamental frequency for three spans × four end conditions
- A sampling check flagging which results the MPU can't reach

### Output as it stands

```
A      = 342.4 mm²
ȳ      = 21.38 mm above the bottom
I      = 166,448 mm⁴
EI     = 33,290 N·m²
mass   = 2.688 kg/m

Whole 24 in track, simply supported : 470 Hz
One 12 in rail, simply supported    : 1,882 Hz
Between sleepers, simply supported  : 16,935 Hz
```

The maths is explained step by step in [docs/06-theory.md](../docs/06-theory.md),
and why the result changed the plan is in [docs/PROBLEMS.md](../docs/PROBLEMS.md).
