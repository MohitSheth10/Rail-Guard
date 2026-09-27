# Logbook

[`Project_LogBook.pdf`](Project_LogBook.pdf) is the handwritten logbook I kept while building Rail-Guard.

It contains the day-to-day calculations, sketches, measurements, decisions and changes to the design.

Some ideas in the logbook were later changed or abandoned, so this is different from the cleaned-up documentation in `docs/`.

## Entries

### 27 September 2026

Reworked the whole GPIO map before the next build pass. HX711 moves off a shared bus onto its own two pins — GPIO4 for DT, GPIO5 for SCK — instead of being wired like it was I2C. Added a second MPU ("Extra MPU") on GPIO6/7, separate from the main one on GPIO8/9 — wired in now for a future accuracy improvement, not part of the detection pipeline yet. The SD card reader gets its own dedicated set of pins (GPIO10-13 for CS/MOSI/SCK/MISO), and the motor driver simplifies down to two control lines: GPIO2 for ENA and ENB together, GPIO3 for IN2 and IN3 together. Redrew the schematic to match before wiring anything up.

### 20 September 2026

Went through the full coding pipeline on the clamped dataset: `daq.py` to log each capture, `fft_analysis.py` to turn it into frequency content, `classify_tightness.py` to try calling each one tight or loose, `statistical_analysis.py` to check the separation was real, and finally `liveclassifytightness.py` to run the same logic live off the sensor's serial stream instead of a saved file. For each scenario — 0, 1, 2, 3, and 4 bolts tight, no fishplate at all, and a stationary motor-off baseline — collected 3 separate readings, 2 minutes each.

Ran an FFT on each capture and tried a few ways to call a joint tight or loose from it. Overall vibration loudness didn't work: a missing fishplate can read about as quiet as a properly tightened joint. Picking the single loudest frequency didn't work either: most readings have two close-strength frequencies that flip which one is louder from reading to reading. What held up was a ratio between two frequency bands:

```
ratio = (energy in 30-60 Hz band) / (energy in 60-100 Hz band)
```

Every 3-4 bolt (secure) reading scored below 0.30, every not-secure reading scored above 0.38, so I set the tight/loose threshold at 0.35, right in the middle of that gap. Also added a check so a near-silent (motor-off) reading gets flagged instead of wrongly called "loose."

### 29 August 2026

Before trusting any data, spent a while debugging the rig itself. The plywood base was moving slightly under its own vibration, so part of what the sensor picked up was the whole board shaking rather than just the joint — fixed that by clamping the base down to the table. Also noticed the MPU wasn't sitting centered on the joint the way it should have been, and that the second rail hadn't been screwed down as firmly as the first, so both of those got fixed too. Added a small counterweight on the far end of the track as well, so the two rail lengths would load and behave more like one continuous piece of real track instead of two short lengths bolted to a board.

Once all of that was sorted, ran a few quick tests with some bolts loose and some tight just to check the readings moved the way they should, then collected the first full clamped-board dataset.

The first look at the data showed a clear change in average vibration as the number of tightened bolts changed. The difference between the more loose states and the more secure states was fairly large. The difference between 3 and 4 tightened bolts was much smaller and wasn't yet reliably separated from normal run-to-run variation.

Also found a timing/recording issue in one baseline file where not all three accelerometer axes were recorded for the full run. Dropped that file rather than patch it.

### 8 August 2026

Bolted both rails onto the plywood base and mounted the motor as a vibration source.

Before doing anything fancy, ran the simplest possible test: a basic sketch just printing raw X, Y, Z accelerometer counts every half second, to prove the MPU was actually talking to the ESP32. That basic test is also what caught the first real surprise of the build — reading the chip's WHO_AM_I register gave `0x70`, not the `0x68` a real MPU-6050 is supposed to return. Turned out the board was actually an MPU-6500 sold under the MPU-6050 name.

Once that basic test passed, finished the 1 kHz MPU capture sketch with timing verification.

Worked out the natural frequency of the rail section by hand and found that the MPU could not reliably reach most of it.

The detection target therefore moved from the rail's natural frequency to the joint response.

### 7 August 2026

The fabricated track came back from the steel shop.

The two 12-inch rails were made from 2-inch T-section with a plate welded along the top to form the rail head, along with the fishplates.

This removed the main physical-build blocker that had been holding up the rest of the experiment.

### Date unsure — sometime between late June and early August 2026

After the perfboard was soldered up, went through it pin by pin to make sure the wiring actually matched the schematic: checked continuity on every connection, then powered up each module on its own (MPU, HX711, SD card, motor driver) and confirmed it responded before trusting the whole board together.

Also went through a few rounds of the track design before it went to the steel shop — rail length, the T-section size, how wide the welded top plate should be, and where the fishplate holes needed to line up so the joint would actually bolt together properly. Some of the back-and-forth on this is in the written logbook and in [docs/PROBLEMS.md](../docs/PROBLEMS.md).

### 27 June 2026

Finished soldering components onto the circuit and finished wiring between components.

### 20 June 2026

Made the project schematic: listed components used, collected spec sheets and pinout diagrams for each, made a pin-mapping sheet for the ESP-32-S3 Zero, then drew the full schematic.

### 13 June 2026

Wired a mini ESP-32-S3 to an MPU-6050 accelerometer for the first time.

### 7 June 2026

Refined the BOM and found cheaper alternatives, making the project more affordable and simpler to execute. Ordered components from Robu.in and Amazon.in.

### 30 May 2026

Made a first rough Bill of Materials. Some components pushed the total cost up significantly.

### 23 May 2026

Researched how the project would actually work -- an MPU-6050 accelerometer connected to a mini ESP-32.

### 16 May 2026

Narrowed ten candidate ideas down to three finalists: an underground mining-robot relay network, Rail-Guard (accelerometers detecting loose fishplate bolts so workers don't have to hammer-tap every bolt by hand), and an automated mechanical power press for smaller sheet-metal companies. Chose Rail-Guard as the most feasible and most interesting of the three.

### 9 May 2026

Worked out a structured process for finding a good problem statement rather than just searching for ideas: literature review against Google Scholar, ResearchGate, and arXiv, checking that no existing project already solves the problem better, and other factors -- feasibility, impact, real-world application, relation to interest.

### 2 May 2026

Started the project. Learned the difference between an idea, a prototype, and a market-ready product, and the feasibility checks to apply to an idea: time, resources, budget. Decided to do an innovation project solving a real problem, in the mechanical/electronics + AI/ML domain. Began ideation -- first three ideas (a dyslexia-detection tool, a sign-language recognizer, an AI sports-coaching system) didn't click or were too niche.
