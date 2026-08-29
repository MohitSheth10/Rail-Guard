# Hardware

This folder contains the drawings, wiring information and parts list for the physical Rail-Guard prototype.

## What I built

The prototype uses a fabricated steel track section with a real bolted fishplate joint.

The rails were made from 2-inch T-section steel with a plate welded along the top to form the rail head.

The track is mounted to a plywood base.

A motor is used as a repeatable vibration source for the bench experiment.

The electronics are soldered onto perfboard rather than left on a breadboard, since the setup is deliberately being vibrated during testing.

## Main hardware

- ESP32-S3 Zero
- MPU-6050/6500 accelerometer board
- MicroSD module
- Motor
- L298N motor driver
- HX711 amplifier
- Load cell
- Fabricated steel track
- Fishplates and bolts
- Plywood base
- Perfboard

## Files

| File/folder | Purpose |
|---|---|
| [`schematic/`](schematic/) | As-built schematic and circuit photos |
| [`wiring.drawio`](wiring.drawio) | Editable wiring diagram |
| [`bill_of_materials.xlsx`](bill_of_materials.xlsx) | Parts list |
| [`track_drawings.pdf`](track_drawings.pdf) | Track and joint drawings |
| [`track_3d_model.html`](track_3d_model.html) | 3D model of the track |

## Current hardware status

- Track and fishplate: built
- Main electronics: assembled
- Accelerometer: tested
- SD card: tested
- Motor vibration: confirmed during the first capture
- Motor + L298N: formal module testing still needs to be completed
- HX711 + load cell: soldered but not yet fully tested
- Circuit box: still to be completed
