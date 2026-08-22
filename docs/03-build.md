[← Back to main README](../README.md)

# Build

How the physical model got made.

---

## The rail problem

I needed track with a real fishplate joint — two rail ends butted together, a steel
plate bolted across both. That's the thing the whole project is about, so it had to
be an actual bolted joint, not a representation of one.

Model railway track is moulded plastic and doesn't have one. Steel suppliers sell
I-beams but nothing at 2-inch scale with a rail profile. I looked for a while
before accepting I'd have to make it.

## Making the rails

I went to a local steel shop and bought **2-inch T-sections**. A T gives you the
base and the vertical web of a rail already. What's missing is the head — the flat
top the wheels run on.

So I had them **weld a plate along the top** of each T-section. That turns it into
something rail-shaped: wide base, thin web, flat head.

![Rails as manufactured](../media/gif/track-manufactured.gif)

Two of these, 12 inches each, giving 24 inches of track total with a joint in the
middle.

**Manufactured 7 August 2026.** That date matters — the track had been the blocker
on almost everything for weeks. Every software plan I wrote had "once the track
model is ready" somewhere in it.

### The catch

The welded plate is 21 mm wide. The base of the T is 50.8 mm. So the finished
section is much wider at the bottom than the top, and that asymmetry turned out to
matter a lot when I came to calculate its natural frequency. Details in
[06-theory.md](06-theory.md) and [PROBLEMS.md](PROBLEMS.md).

## Fishplates

Steel plates, 4 inches long, drilled for four bolts — two into each rail end. They
sit against the web on both sides of the joint, same as the real thing.

![Fishplate joint](../media/img/track-fishplate-joint-closeup.jpg)

You can see the weld bead running along the top of each rail in that photo, and the
joint gap between the two rail ends. The bolts are what get loosened and tightened
during testing, so they're the actual subject of the experiment.

## Base

Plywood, cut to take both rails at 4.25-inch gauge. Holes are drilled through the
rail base flanges so they can be screwed down.

**Mounted 8 August 2026.** I've left the screws out for now — the model is heavy
enough that it doesn't shift much on its own, and being able to lift a rail off
makes it easier to try different sensor positions. That'll change once testing
settles down.

![Track on the base](../media/img/track-full-on-base.jpg)

The base can be cut into separate planks later so it looks more like sleepers on
ballast. Cosmetic, not urgent.

## Cart

A four-wheel chassis with its own AA battery pack, running on the rails. It stands
in for a train — enough weight and enough of a bump crossing the joint to set
things vibrating.

![Cart running on the track](../media/gif/cart-rolling-test.gif)

It's not trying to be a scale model of anything. It just has to load the joint the
same way every run, because repeatability is what the experiment depends on.

## Vibration source

**8 August 2026** — mounted the motor directly onto one of the rails, so it can
shake the track without needing the cart to roll. Steadier and more repeatable than
pushing a cart by hand, and it means I can excite the rail on demand while testing
the sensor.

---

## Still to do

- Buy a spanner sized for the fishplate bolts
- Improve the cart wiring and add a proper switch
- Decide and mark the final sensor mounting position
- Measure the real flange and web thickness with a caliper

---

[← Design](02-design.md) · [Electronics →](04-electronics.md)
