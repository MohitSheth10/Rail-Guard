[← Back to main README](../README.md)

# Theory — natural frequency of the rail section

Working out what frequency the rail rings at, and what that means for the sensor.

Script: [`analysis/natural_frequency.py`](../analysis/natural_frequency.py)

---

## Why bother

Detection works off frequency, so an FFT full of numbers is meaningless without
knowing what to expect. Calculating it up front gives three things: a sanity check
on the sensor, the sampling rate the firmware needs, and — as it turned out — proof
that the original plan wouldn't work.

## The section

Fabricated from 2-inch T-section with a plate welded on top.

| | mm |
|---|---|
| Top flange width (welded plate) | 21.0 |
| Bottom flange width (T base) | 50.8 |
| Web height | 50.8 |
| Flange thickness | 3.0 *(assumed)* |
| Web thickness | 2.5 *(assumed)* |
| **Total height** | **56.8** |

The top and bottom flanges are different widths, so this is **not** a symmetric
I-beam and the usual textbook formula doesn't apply.

## Step 1 — find the centroid

When a beam bends, the top compresses and the bottom stretches. Between them is a
line that does neither, and that's the line the beam bends around. It sits at the
section's balance point.

Split the section into three rectangles, multiply each area by its own height above
the bottom, add up, divide by total area.

| Piece | Area (mm²) | Height of centre (mm) | A × y |
|---|---|---|---|
| Bottom flange | 152.4 | 1.5 | 229 |
| Web | 127.0 | 28.4 | 3,607 |
| Top flange | 63.0 | 55.3 | 3,484 |
| **Total** | **342.4** | | **7,319** |

```
ȳ = 7,319 / 342.4 = 21.4 mm above the bottom
```

Mid-height is 28.4 mm, so the balance line sits 7 mm lower than it would on a
symmetric section. That's the welded plate being narrower than the base.

## Step 2 — second moment of area

Each rectangle contributes its own stiffness `b·h³/12`, plus a distance bonus
`A·d²` for how far it sits from the centroid. The second term is the parallel axis
theorem, and it usually dominates.

| Piece | Own stiffness | d (mm) | A·d² | Total |
|---|---|---|---|---|
| Bottom flange | 114 | −19.9 | 60,228 | 60,342 |
| Web | 27,312 | +7.0 | 6,259 | 33,571 |
| Top flange | 47 | +33.9 | 72,488 | 72,535 |

```
I = 166,448 mm⁴  =  1.6645 × 10⁻⁷ m⁴
```

Worth looking at the top flange row. Its own stiffness is 47 — it's a thin strip,
almost nothing. But it sits 34 mm from the balance line, and that distance alone
contributes 72,488. It's the biggest single contributor to the beam's stiffness,
and nearly all of that comes from where it is rather than what it is.

That's the entire reason rails and I-beams are shaped the way they are.

## Step 3 — frequency

```
        λ²        ⎯⎯⎯⎯⎯⎯⎯
f  =  ──────  ×  √ EI / (m·L⁴)
        2π
```

Mild steel: `E` = 200 GPa, density 7850 kg/m³.

```
EI = 200×10⁹ × 1.6645×10⁻⁷  =  33,290 N·m²
m  = 7850 × 3.424×10⁻⁴      =  2.688 kg/m
```

`λ²` depends on how the ends are held — 3.52 cantilever, 9.87 simply supported,
15.42 fixed-pinned, 22.37 fixed-fixed (and free-free).

### Results

| Span | Cantilever | Simply supported | Fixed–pinned | Fixed–fixed |
|---|---|---|---|---|
| 609.6 mm (whole track) | 168 Hz | **470 Hz** | 735 Hz | 1,066 Hz |
| 304.8 mm (one rail) | 670 Hz | **1,882 Hz** | 2,940 Hz | 4,265 Hz |
| 101.6 mm (sleeper gap) | 6,032 Hz | **16,935 Hz** | 26,461 Hz | 38,389 Hz |

Note how hard span matters. `L⁴` is under the square root, so frequency goes as
`1/L²` — halve the span, quadruple the frequency. Getting the span right matters
more than getting the thicknesses right.

## What this ruled out

The MPU's accelerometer samples at **1000 Hz maximum**. Nyquist puts the usable
ceiling at 500 Hz, realistically lower.

Every number in that table except the two smallest is out of reach. The sensor
cannot hear the rail ring, and if I'd pointed an FFT at it anyway, aliasing would
have handed me a plausible-looking low frequency that meant nothing.

So detection targets the **joint** instead — the fishplate, bolts and base moving
together, which is a heavier and much lower-frequency system. A loose bolt doesn't
change the stiffness of the steel. It changes how the two rail ends move against
each other, and that's the low-frequency signal the MPU can actually see.

Full account in [PROBLEMS.md](PROBLEMS.md).

## To verify

- Measure the real flange and web thickness and re-run the script
- Tap test with a phone spectrum analyser — a phone mic reaches ~20 kHz, so unlike
  the MPU it can hear the ring. Resting on foam is free-free, so expect roughly
  4.3 kHz for a single rail
- Compare measured against calculated and write down the gap

---

[← Software](05-software.md) · [Problems →](PROBLEMS.md)
