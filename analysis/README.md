# Analysis

This is where I turn the ESP32's stream of numbers into data I can actually use.

The folder currently contains two main scripts:

- `daq.py` — records vibration data from the ESP32 and saves it for later
- `natural_frequency.py` — calculates the rail's section properties and estimated natural frequency

---

## `daq.py`

The ESP32 can print sensor values to the Serial Monitor, but watching numbers scroll past isn't very useful when running an experiment.

`daq.py` records the data to CSV so a run can be looked at afterwards.

### Running it

```bash
python daq.py
```

The script needs `pyserial`:

```
pip install pyserial
```

Set the board's COM port at the top of the file before running it.

### What it does

- Reads the vibration data coming from the ESP32
- Saves each row to a timestamped CSV file
- Works with the columns currently being sent by the board
- Shows the number of rows and measured rate while recording
- Flushes and closes the file cleanly when the capture is stopped

### First result

The first proper capture showed a quiet signal while the setup was stationary and a clear increase in vibration when the motor started. That confirmed that the basic chain — sensor → ESP32 → computer → CSV — was actually working. It did not prove that the system could distinguish a tight joint from a loose one. That is what the controlled dataset is for.

This `daq.py` is the simpler, earlier version of the logger. The one actually used to collect the datasets in `code/Accurate Readings/` and `code/Inaccurate Readings/` is [`code/daq.py`](../code/daq.py), which added stall detection and rate checking against the ESP32's own timing. See [`code/README.md`](../code/README.md) for how the two differ.

## `natural_frequency.py`

This script came from my original plan. I initially thought the easiest way to detect a loose joint would be to look for a change in the rail's natural frequency. So I calculated it before doing the main experiment.

The calculation gave a frequency range of roughly 470 Hz to 17 kHz, depending on the rail support conditions.

Then I checked the accelerometer's sampling limit. At about 1 kHz sampling, the useful frequency range ends around 500 Hz because of the Nyquist limit. That meant most of the frequencies I had calculated were outside what the sensor could reliably measure.

That result changed the direction of the project. Instead of trying to measure the rail's full natural-frequency response, I started looking at the vibration and movement of the joint itself.

### Running it

```
python3 natural_frequency.py
```

It uses only Python's standard library. The dimensions are set near the top of the file. The script distinguishes between measured/confirmed dimensions and dimensions that are still assumptions.

The detailed working and reasoning are in [`docs/06-theory.md`](../docs/06-theory.md).

## Current data

The latest controlled data is in: [`../code/Accurate Readings/`](../code/Accurate%20Readings/)

Earlier runs are in: [`../code/Inaccurate Readings/`](../code/Inaccurate%20Readings/)

The older data is intentionally kept because it helped expose the board-movement problem. It should not be used as the main basis for the final tight-vs-loose conclusion.

The current controlled data shows a clear change in average vibration as the bolt state changes. The larger loose-vs-secure differences are easier to see than the difference between 3 and 4 tightened bolts. More data is needed before a final threshold can be chosen.

There is also a recording/timing issue in one of the runs where not all accelerometer axes were captured for the entire test. That needs to be fixed before the next dataset is treated as final.
