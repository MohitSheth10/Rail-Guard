"""
Rail Guard - Natural frequency of the mild steel rail section
-------------------------------------------------------------
Measure your actual rail with a vernier caliper, put the numbers in
MEASUREMENTS below, and run this file.

Everything is in millimetres. The script converts to metres itself.
"""

import math

# ============================================================
#  1. MEASUREMENTS  --  replace these with your real caliper readings
# ============================================================
# Current values are from RailGuard_Track_3D.html.
# The ones marked ASSUMED were never measured. Measure them.

TOP_FLANGE_WIDTH = 21.0     # CONFIRMED - 2.1 cm, the cart rides on this
BOT_FLANGE_WIDTH = 50.8     # CONFIRMED - 2 in
WEB_HEIGHT       = 50.8     # CONFIRMED - 2 in (clear height between flanges)
FLANGE_THICKNESS = 3.0      # ASSUMED  <-- measure this
WEB_THICKNESS    = 2.5      # ASSUMED  <-- measure this

# Material: mild steel
E   = 200e9      # Young's modulus, Pa
RHO = 7850.0     # density, kg/m^3

# Spans you want to check (mm). A span is the free distance between supports.
SPANS = {
    "whole 24 in track":        609.6,
    "one 12 in rail piece":     304.8,
    "between sleepers (4 in)":  101.6,
}

# How the ends are held. lambda^2 values from standard beam theory.
END_CONDITIONS = {
    "cantilever (one end fixed)": 1.875 ** 2,
    "simply supported":           math.pi ** 2,
    "fixed-pinned":               3.927 ** 2,
    "fixed-fixed (both clamped)": 4.730 ** 2,
}

MPU_SAMPLE_RATE = 1000.0   # MPU-6050 accelerometer maxes out at 1 kHz


# ============================================================
#  2. SECTION PROPERTIES
# ============================================================
# The section is ASYMMETRIC - the top flange is narrower than the bottom.
# So the neutral axis is NOT at mid-height, and you cannot use the simple
# symmetric I-beam formula. You have to find the centroid first, then use
# the parallel axis theorem.

total_height = WEB_HEIGHT + 2 * FLANGE_THICKNESS

# Break the section into 3 rectangles: (width, height, height of its own
# centre above the bottom of the section)
parts = [
    ("bottom flange", BOT_FLANGE_WIDTH, FLANGE_THICKNESS, FLANGE_THICKNESS / 2),
    ("web",           WEB_THICKNESS,    WEB_HEIGHT,       FLANGE_THICKNESS + WEB_HEIGHT / 2),
    ("top flange",    TOP_FLANGE_WIDTH, FLANGE_THICKNESS, total_height - FLANGE_THICKNESS / 2),
]

# Area
area = sum(b * h for _, b, h, _ in parts)

# Centroid height, measured up from the bottom of the section
y_bar = sum(b * h * y for _, b, h, y in parts) / area

# Second moment of area about the centroid.
#   own I of each rectangle  +  its area x (distance to centroid)^2
second_moment = sum(
    (b * h ** 3 / 12) + (b * h) * (y - y_bar) ** 2
    for _, b, h, y in parts
)

print("=" * 62)
print("SECTION PROPERTIES")
print("=" * 62)
for name, b, h, y in parts:
    print(f"  {name:<15} {b:6.2f} x {h:5.2f} mm   centre at y = {y:6.2f} mm")
print()
print(f"  Total height           H  = {total_height:10.2f} mm")
print(f"  Area                   A  = {area:10.2f} mm^2")
print(f"  Centroid above bottom  y  = {y_bar:10.2f} mm")
print(f"  Second moment of area  I  = {second_moment:10.0f} mm^4")

# Convert to SI
I_si    = second_moment * 1e-12          # mm^4 -> m^4
area_si = area * 1e-6                    # mm^2 -> m^2
mass_per_length = RHO * area_si          # kg/m
EI = E * I_si                            # N.m^2

print()
print(f"  I  = {I_si:.4e} m^4")
print(f"  EI = {EI:,.0f} N.m^2")
print(f"  Mass per metre = {mass_per_length:.3f} kg/m")


# ============================================================
#  3. NATURAL FREQUENCY
# ============================================================
#            lambda^2       /  E I
#     f  =  ----------  x  / -------
#              2 pi      \/   m L^4

def natural_frequency(lambda_sq, span_m):
    return (lambda_sq / (2 * math.pi)) * math.sqrt(EI / (mass_per_length * span_m ** 4))


print()
print("=" * 62)
print("FUNDAMENTAL NATURAL FREQUENCY (first mode)")
print("=" * 62)

for span_name, span_mm in SPANS.items():
    span_m = span_mm / 1000.0
    print(f"\n  Span = {span_mm:.1f} mm   ({span_name})")
    for cond_name, lambda_sq in END_CONDITIONS.items():
        f = natural_frequency(lambda_sq, span_m)
        flag = "" if f < MPU_SAMPLE_RATE / 2 else "   <-- above what the MPU can see"
        print(f"      {cond_name:<28} {f:9.0f} Hz{flag}")

print()
print("=" * 62)
print("SAMPLING CHECK")
print("=" * 62)
print(f"  MPU-6050 accelerometer output rate: {MPU_SAMPLE_RATE:.0f} Hz max")
print(f"  Highest frequency it can resolve:   {MPU_SAMPLE_RATE / 2:.0f} Hz (Nyquist limit)")
print(f"  Realistic usable ceiling:           ~{MPU_SAMPLE_RATE / 3:.0f} Hz")
print()
print("  Anything above that ceiling will not appear in your FFT, or worse,")
print("  will fold back and appear as a fake low frequency (aliasing).")
print("=" * 62)
