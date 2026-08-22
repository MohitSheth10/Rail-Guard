[← Back to main README](../README.md)

# Concept

---

## The problem

Rails come in fixed lengths. Where two lengths meet, they're joined by a
**fishplate** — a steel bar laid against the web of both rails and bolted through,
usually with four or six bolts. It holds the two rail ends in line so a wheel can
cross the gap without dropping.

Those bolts loosen. Trains pass, the joint flexes, temperature swings the rail
length back and forth, and over enough cycles the nuts back off. A loose fishplate
joint lets the rail ends move independently. The gap opens, the alignment goes, and
the joint starts hammering itself apart under every wheel.

Joint failures are a known cause of derailments. They're also slow — a bolt doesn't
loosen overnight, which means there's a long window where the problem exists and
could be found.

## How it's found now

By eye, mostly. Someone walks the section and looks at the joints, or a
track-recording vehicle measures rail geometry and picks up the consequences of a
bad joint rather than the joint itself.

Both work. Both are expensive per kilometre, and both mean a given joint gets
looked at every few weeks at best.

## The idea

Put an accelerometer on something that's already travelling the line and let it
listen.

A wheel crossing a tight joint and a wheel crossing a loose joint don't sound the
same. The loose one has more movement in it — the rail ends shift against each
other, and the impact is sharper and less damped. That difference shows up in the
vibration signal.

If a sensor can tell those two apart reliably, then every train that passes becomes
an inspection, and the map of which joints need attention updates continuously
instead of every few weeks.

## Scope of this build

A working bench model, not a product:

- 24 inches of fabricated track with one real bolted fishplate joint
- A cart that rolls over the joint
- An MPU accelerometer reading the vibration
- An ESP32-S3 sampling it and deciding loose or tight
- An LED to show the result

If the model can tell a loose bolt from a tight one, the principle holds.

## What already exists

Worth being honest about what's new here and what isn't.

Vibration-based bolt-looseness detection is an active research area — there's a
reasonable body of published work on using accelerometers and machine learning to
detect loose bolted joints, mostly in structural engineering rather than rail.
Commercially, companies like Sperry Rail run dedicated inspection vehicles, and
most large rail operators use track geometry cars.

What those have in common is that they're dedicated inspection equipment. The angle
here is a cheap sensor on ordinary rolling stock, aimed specifically at the
fishplate joint.

A proper literature review is still outstanding — 5 to 8 papers, noting for each
what sensor was used, what was measured, and how well it worked. That's the next
research task.

---

[Design →](02-design.md)
