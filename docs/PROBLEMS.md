—[← Back to main README](../README.md)

# Problems

Everything that went wrong, in the order it went wrong. This is the most useful
file in the repo, because most of what I learned came from here rather than from
the parts that worked.

---

## Nobody sells the rail I needed

The first real wall. I needed a piece of track with a proper fishplate joint —
two rail ends, a plate across them, bolts through the web. Model railway track
doesn't have that. It's moulded plastic with the rail shape suggested rather than
built. Structural steel suppliers sell I-beams, but not at 2-inch scale, and not
with a rail profile.

I spent a while looking for something to buy before accepting there wasn't one.

**What I did.** Went to a local steel shop, bought 2-inch T-sections, and had them
weld a flat plate along the top of each to make the rail head. A T-section gives
you the base and the web. The welded plate turns it into something rail-shaped.

It worked. It also created two problems I didn't see coming.

---

## The welded plate made the section asymmetric

The plate I had welded on is 21 mm wide. The base of the T is 50.8 mm. So the
finished rail is much wider at the bottom than the top.

I didn't think about this at all while designing it. It only mattered later, when
I tried to calculate the natural frequency and found that every textbook formula
for an I-beam assumes the top and bottom flanges are the same.

They aren't. So the neutral axis — the line the beam bends around — isn't at
mid-height. It sits 21.4 mm up from the bottom instead of 28.4 mm. Before I could
calculate anything I had to find the centroid, then apply the parallel axis
theorem to each part separately.

More work than I expected from a shortcut at a steel shop. Full working in
[06-theory.md](06-theory.md).

---

## I never measured the steel

The design file lists flange thickness as 3 mm and web thickness as 2.5 mm. Both
of those are assumptions I made while drawing it. Nobody put a caliper on the
actual part.

Every frequency number in this repo is built on those two numbers, so every
frequency number is provisional until I measure the real thing. Noting it here so
I don't quietly forget and present a guess as a result.

---

## The model is too heavy to carry

Mild steel, two rails, plus a plywood base. It's solid, which is good for the
physics and bad for getting it to school. Carrying it in and back every week isn't
realistic, so it needs somewhere to live.

Not a technical problem, but it's shaped the schedule more than most technical
problems have.

---

## The sensor cannot hear the thing I was trying to measure

This is the one that nearly wasted a fortnight.

The plan was: work out the rail's natural frequency, then look for that frequency
in the accelerometer data and watch it shift when a bolt loosens.

I did the calculation. Depending on how the rail is supported, the fundamental
comes out somewhere between **470 Hz and 17 kHz** — 470 Hz across the full 24-inch
track, about 1.9 kHz for a single 12-inch piece, and roughly 17 kHz across the
4-inch gap between sleepers.

Then I checked what the MPU-6050 can actually do. Its accelerometer updates at
**1000 Hz maximum**. That's a hardware limit, not a setting. Nyquist says the
highest frequency you can trust is half the sample rate, so 500 Hz, and in practice
less.

The sensor physically cannot hear the rail ring.

Worse, it doesn't fail quietly. Anything above 500 Hz gets folded back down and
shows up in an FFT as a completely convincing low frequency that isn't real. If I
hadn't checked, I would have built the detection logic on a number that was an
artifact, and it would have looked like it was working.

**What I changed.** The rail's own ringing isn't the target any more. A loose bolt
doesn't change the stiffness of the steel — the steel is the same either way. What
changes is the joint: the two rail ends start moving against each other, and the
fishplate assembly on a plywood base is a much heavier, floppier system than the
rail alone. That moves in the tens-to-low-hundreds of Hz, which is comfortably
inside what the MPU can see.

So the calculation didn't get thrown away. It told me where *not* to look, which
turned out to be the more useful answer.

---

## The sensor isn't the sensor I thought it was

While bringing up the high-rate sketch, the `WHO_AM_I` register came back as
`0x70`. An MPU-6050 returns `0x68`.

`0x70` is an **MPU-6500** — a newer chip, sold on GY-521 boards under the
MPU-6050 name. Register-compatible for the basics, which is why every earlier test
passed and I never noticed.

It matters here because the two chips put the accelerometer's low-pass filter in
**different registers**. On the 6050 it's in `CONFIG (0x1A)`. On the 6500 it's in
`ACCEL_CONFIG2 (0x1D)`, and `CONFIG` only affects the gyro. Setting the 6050
register on a 6500 does nothing to the accelerometer, so I'd have been running at
whatever bandwidth it defaulted to and wouldn't have known.

The sketch now writes both registers and identifies the chip at startup. Slightly
in my favour, too: the 6500's widest accelerometer bandwidth is 460 Hz against the
6050's 260 Hz.

Lesson: read `WHO_AM_I` before trusting the label on the board.

---

## The default MPU sketch runs 500 times too slow

My first working MPU test had a `delay(500)` in the loop. Two readings a second.
Completely fine for checking the sensor is alive, completely useless for vibration.

Getting from 2 Hz to 1000 Hz meant fixing four separate things:

1. **I2C bus speed.** Arduino defaults to 100 kHz. Not enough headroom to move six
   bytes every millisecond. Set to 400 kHz.
2. **The sensor's own registers.** Enable the DLPF so the internal base rate is
   1 kHz, then `SMPLRT_DIV = 0` to divide by one.
3. **No `delay()` anywhere.** The loop now works to absolute deadlines — sample `i`
   is due at `t0 + i × 1000 µs` — so timing errors don't pile up over the burst.
4. **No printing during capture.** This one is a trap. Serial at 115200 baud can't
   keep up with 1 kHz, so a `Serial.print` inside the loop silently stretches the
   intervals. The data still looks fine. The FFT is wrong. The sketch now buffers
   the whole 2-second burst in RAM and dumps it afterwards.

The sketch measures its own achieved rate and jitter and prints PASS or FAIL, so I
never have to take the timing on trust.

---

## Serial output was silently blank on the S3

Small one, but it cost an evening. The ESP32-S3 Zero has a single native USB port.
If you build with USB mode set to OTG and "USB CDC On Boot" disabled, `Serial` goes
out the hardware UART pins instead of the USB port, and the Serial Monitor just
sits there empty. No error, no warning.

There's now a compile-time guard in the sketch that catches exactly that
combination and fails the build with a message telling you which setting to change.

---

## Still open

- Flange and web thickness never measured
- HX711 soldered but never tested — no load cell connected yet
- Motor driver never tested
- No idea yet whether the tight-vs-loose difference will actually be big enough to
  threshold cleanly. That's the next experiment, and it's the one the whole project
  rests on.
