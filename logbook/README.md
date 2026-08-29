# Logbook

[`Project_LogBook.pdf`](Project_LogBook.pdf) is the handwritten logbook I kept while building Rail-Guard.

It contains the day-to-day calculations, sketches, measurements, decisions and changes to the design.

Some ideas in the logbook were later changed or abandoned, so this is different from the cleaned-up documentation in `docs/`.

## Recent entries

### 29 August 2026

Fixed the board-drift problem by clamping the plywood base down.

Collected the first full clamped-board dataset.

The first look at the data showed a clear change in average vibration as the number of tightened bolts changed. The difference between the more loose states and the more secure states was fairly large. The difference between 3 and 4 tightened bolts was much smaller and is not yet reliably separated from normal run-to-run variation.

Also found a timing/recording issue in one baseline file where not all three accelerometer axes were recorded for the full run. This still needs to be fixed before relying on the next round of data.

### 8 August 2026

Bolted both rails onto the plywood base and mounted the motor as a vibration source.

Finished the 1 kHz MPU capture sketch with timing verification.

Worked out the natural frequency of the rail section by hand and found that the MPU could not reliably reach most of it.

The detection target therefore moved from the rail's natural frequency to the joint response.

Also found that the sensor on the board was actually an MPU-6500 rather than an MPU-6050.

### 7 August 2026

The fabricated track came back from the steel shop.

The two 12-inch rails were made from 2-inch T-section with a plate welded along the top to form the rail head, along with the fishplates.

This removed the main physical-build blocker that had been holding up the rest of the experiment.
