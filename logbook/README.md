[← Back to main README](../README.md)

# Logbook

[`Project_LogBook.pdf`](Project_LogBook.pdf) — the handwritten project logbook,
scanned. Day-to-day notes, sketches and working from the whole build.

## Recent entries

**29 August 2026** — Fixed the board-drift error: clamped the plywood base down
with two clamps so it can't creep under its own vibration during a run. Collected
the first full clamped-board dataset — three one-minute stationary baselines, three
one-minute runs at each bolt state from 0 through 4 bolts tightened, and three runs
with the fishplate removed entirely. First look at the numbers is encouraging:
average vibration drops in a clean, consistent line as more bolts are tightened,
and the three repeats at each state agree closely with each other. The gap between
badly loose (0–1 bolts) and reasonably secure (3–4 bolts) is large and easy to see;
the gap between 3 bolts and 4 bolts is not — smaller than the normal run-to-run
noise, so the sensor can't yet split those two apart. Also turned up a timing
glitch in one baseline file (only 2 of 3 sensor axes recorded for that entire run)
— the same intermittent issue behind the earlier 1000 Hz/2500 Hz inconsistency,
still unresolved in firmware and worth chasing down before the next data pass.

**7 August 2026** — Track model came back from the steel shop. Two 12-inch rails,
fabricated from 2-inch T-section with a plate welded along the top to form the head,
plus fishplates. This had been the blocker on almost everything for weeks.

**8 August 2026** — Bolted both rails onto the plywood base and mounted the motor
on one rail as a vibration source. Finished the 1 kHz MPU capture sketch, with
timing verification built in. Worked out the natural frequency of the rail section
by hand and found the MPU can't reach it — the detection target moves to the joint
response instead. Found the sensor is actually an MPU-6500, not a 6050.
