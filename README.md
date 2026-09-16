# Rail-Guard

**Mohit Sheth · Dhirubhai Ambani International School, Mumbai · DAIS × OMOTEC Innovation Programme**

Rail-Guard is an early-warning system for railway track joints. It listens to the vibration a *fishplate joint* makes as a train rolls over it, and works out whether the bolts holding that joint together are loose — automatically, with nobody having to walk the track or tap anything.

---

## Why I chose this

A fishplate is the steel plate that clamps two rail ends together — four bolts per plate, eight per joint. Every train that passes shakes those bolts a little looser over time. The way this is checked today hasn't really changed in decades: a worker walks the track on foot and taps each bolt with a hammer, listening for the dull sound a loose one makes. It works, but it's slow and completely blind — the inspector has no way of knowing which bolt is loose until he's already standing on top of it.

The whole point of my project is to remove the tapping. If my system needed a person to go and tap each joint, it wouldn't be solving anything. So it has to work from the vibration a *normal passing train* already makes.

---

## The idea, in one line

**A bolted joint is like a guitar string.** Tighten a guitar string and it plays a higher note; loosen it and the note drops. A bolted joint does the same — a tight joint is stiff and vibrates cleanly, while a loose joint goes floppy and *rattles*. The worker with his hammer is really just listening to that change in pitch. I'm detecting the same thing with a sensor and some code, from train vibration instead of a hammer.

---

## How it works

The system sits idle, watching the vibration level. When a train arrives, the vibration jumps — the system notices this on its own, wakes up, records a short burst from the sensor, and analyzes it. No button, no human.

To analyze the burst I use an **FFT** (Fast Fourier Transform) — think of it as a machine that takes a messy mix of vibration and tells you which "wobble speeds" (frequencies) are inside it, and how strong each one is.

Here's the part that took me a while to understand, and it's the core of the project:

- My motor spins at about 4000 RPM, which is roughly **67 shakes per second (67 Hz)**. That's the rhythm it *drives* the track at.
- - A tight joint passes that vibration through cleanly — the FFT shows basically **one clean peak at 67 Hz**.
  - - A loose joint **rattles**. Metal knocks against metal, which adds extra peaks at multiples of 67 Hz (134, 200, 268…). So a loose joint shows **67 Hz plus a mess of extra spikes**, and it usually lets *less* total vibration through.
   
    - So my two main clues for "loose vs tight" are **how much vibration gets through (RMS amplitude)** and **how messy/rattly the signal is (harmonic content)** — not just a single frequency. That mess is the fingerprint of a loose bolt.
   
    - ---

    ## The model I'm building

    A model track roughly the length of a study table, with **one real fishplate joint I can loosen and tighten**. Everything that matters is **metal, not plastic** — plastic absorbs vibration instead of carrying it, so the signal I'm hunting simply wouldn't exist.

    | Part | Material |
    |------|----------|
    | Rails | Aluminum angle |
    | Fishplate | Mild steel flat bar |
    | Bolts | Steel M6 (loosened/tightened by a measured number of turns) |
    | Sleepers / baseboard | Wood / MDF, on rubber feet |

    **The most important design decision:** the motor goes on **one** rail and the sensor on the **other** rail, across the joint from it. That forces the vibration to travel *through* the joint to reach the sensor — so the joint's condition directly controls what the sensor sees. It also mirrors real life: a train's wheels shake the rail, and that vibration has to cross the joint.

    ---

    ## Hardware

    | Component | Role |
    |-----------|------|
    | ESP32-S3 Mini | Main controller (runs the FFT, has WiFi) |
    | MPU-6050 accelerometer | Reads the joint's vibration over I²C |
    | 775 DC 12V vibration motor + L298N driver | Simulates a passing train |
    | XY-3606 buck converter | Steps 12V down to 5V |
    | MicroSD module | Logs every reading |
    | Green / red LEDs | Green = OK, Red = loose |

    I'm also testing a **piezo disc** as an alternative sensor, because it can pick up higher frequencies than the MPU-6050 — the two run side by side so I can compare them with real data instead of guessing.

    ---

    ## Where I'm at right now

    - Idea finalized, research done, bill of materials complete, parts received
    - - ESP32-S3 talking to the accelerometer over I²C; first live readings working
      - - SD card logging tested
        - - Model track being built; motor wiring on the way
          - - Next: capture bursts, run the FFT, and build the loosening curve (tight → loose, measured in bolt turns) that proves the concept
           
            - ---

            ## Scope (on purpose)

            Right now this is a **loose-bolt detector** — one clean, provable claim. Deliberately parked for later so I can do the core thing properly first:

            - Over-tightening detection (the load cell / HX711 force sensing)
            - - A live WiFi dashboard
              - - A second fishplate joint for a side-by-side demo
               
                - ---

                ## What I've learned so far

                The hardware was the steep part. Getting usable data meant actually understanding I²C, sample rates, and why the sensor's own built-in filter was quietly deleting the exact high-frequency vibration I needed. The biggest lesson was about *frequencies* — realizing that my motor can't reach the joint's natural ringing frequency, so I had to detect looseness from rattling and transmitted energy instead. Working that out felt like the moment the project actually made sense.

                ---

                ## Repository structure

                ```
                Rail-Guard/
                ├── README.md               — this overview
                ├── analysis/               — Python scripts + data analysis
                ├── code/                   — Arduino / ESP32 sketches
                ├── hardware/               — block diagram, wiring, bill of materials
                ├── docs/                   — write-ups, one per build stage
                ├── logbook/                — dated session-by-session log
                ├── media/                  — photos and videos of the build
                ├── presentations/          — milestone slide decks
                └── specification_sheets/   — component datasheets
                ```

                **File naming:** `RG_<stage>_<type>_<name>_v<version>` — e.g. `RG_S1_DOC_Research-Summary_v1.docx`, `RG_S4_VID_Bench-Test_v1.mp4`. Stages S1-S6 follow the build plan; milestones M1-M3 are the presentation checkpoints.
                
