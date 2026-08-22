[← Back to main README](../README.md)

# Design

Dimensions and drawings for the track model.

---

## Overall

| | |
|---|---|
| Total track length | 24 in (610 mm) — two 12 in pieces |
| Gauge (rail centre to centre) | 4.25 in (108 mm) |
| Sleeper spacing | ~4 in (102 mm) |
| Fishplate length | 4 in (102 mm) |
| Bolts per joint | 4 |

## Rail section

| | mm | Source |
|---|---|---|
| Total height | 56.8 | derived |
| Web height | 50.8 | confirmed — 2 in T-section |
| Bottom flange width | 50.8 | confirmed — 2 in |
| Top flange width | 21.0 | confirmed — 2.1 cm welded plate |
| Flange thickness | 3.0 | **assumed** |
| Web thickness | 2.5 | **assumed** |

The last two have never been measured with a caliper. They came from the drawing,
not the part. Everything in [06-theory.md](06-theory.md) depends on them, so
they're the first thing to check.

### Why it's asymmetric

The rail is a 2-inch T-section with a plate welded along the top — see
[03-build.md](03-build.md). The T gives the base and the web. The welded plate
makes the head, and it's narrower than the base.

Real rail is asymmetric too, for the same reason: a wide foot to spread load into
the sleeper, a narrow head for the wheel. So the shape is right even though it came
about by accident of fabrication.

It does mean the neutral axis isn't at mid-height, which made the frequency
calculation considerably more involved than expected.

## Fishplate

Bar stock, 4 in long, ~1.8 in tall so it sits inside the web height without
fouling the flanges. Four bolt holes. Deliberately thin — the joint has to be able
to flex, because that flex is the signal.

Bolt positions are offset either side of the joint centre, with a gap left in the
middle for the MPU mount.

## Sensor mounting

Reserved a 40 mm gap at the centre of the joint for the accelerometer. Exact
position isn't fixed yet — a few spots need trying to see which gives the clearest
difference between tight and loose. Once chosen it gets marked, because it has to
go back the same way every run or the data isn't comparable.

## Files

| File | What it is |
|---|---|
| `RailGuard_Track_3D.html` | Interactive 3D model — open in a browser, drag to rotate |
| `RailGuard_Track_Drawings.pdf` | Dimensioned drawings, sent to the fabricator |
| `Rail Track Dimensions.pdf` | Reference dimensions for real track |
| `Railway_Track_Specs_Reference.pptx` | Background on real rail sections |

*(These live in the project folder; add them to the repo if you want them here.)*

---

[← Concept](01-concept.md) · [Build →](03-build.md)
