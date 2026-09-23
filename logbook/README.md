# Logbook

[`Project_LogBook.pdf`](Project_LogBook.pdf) is the handwritten logbook I kept while building Rail-Guard.

It contains the day-to-day calculations, sketches, measurements, decisions and changes to the design.

Some ideas in the logbook were later changed or abandoned, so this is different from the cleaned-up documentation in `docs/`.

## Recent entries

### 20 September 2026

Ran an FFT on each vibration capture and tried a few ways to call a joint tight or loose from it. Overall vibration loudness didn't work -- a missing fishplate can read about as quiet as a properly tightened joint. Picking the single loudest frequency didn't work either -- most readings have two close-strength frequencies that flip which one is louder from reading to reading. What held up: the ratio of vibration energy in the 30-60 Hz band to the 60-100 Hz band. Every 3-4 bolt (secure) reading scored below 0.30, every not-secure reading scored above 0.38, so I set the tight/loose threshold at 0.35. Also added a check so a near-silent (motor-off) reading gets flagged instead of wrongly called "loose."

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

*(No dated log entries between this point and 27 June -- see [docs/PROBLEMS.md](../docs/PROBLEMS.md) for what the build ran into in between.)*

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
