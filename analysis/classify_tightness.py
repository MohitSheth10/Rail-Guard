"""
classify_tightness.py -- Rail-Guard tight/loose classifier

fft_analysis.py gives you the raw numbers for a reading. This script takes
that a step further and answers the actual question: is the fishplate
securely tightened, or not?

How it decides, in plain terms:

  We tried a few different numbers from the FFT and checked which one
  actually holds up across every reading we have (0 to 4 bolts tight, and
  the fishplate removed entirely):

    - Overall "how loud is the shake" (RMS) isn't reliable by itself -- a
      completely missing fishplate can read about as quiet as a properly
      tightened joint. Using RMS alone risks missing the worst failure.

    - "Which single frequency is loudest" isn't reliable either -- most
      readings contain two frequencies close in strength, roughly a slow
      ~39 Hz beat and a faster ~79 Hz echo of it, and which one comes out
      slightly louder can flip from one reading to the next even at the
      same bolt count.

    - What DOES hold up: the balance between those two, measured as a
      ratio of vibration energy (this is fft_analysis.py's low_high_ratio):

          ratio = energy in the 30-60 Hz band / energy in the 60-100 Hz band

      A securely tightened joint puts most of its energy into the faster
      ~79 Hz echo, so the ratio comes out low. A joint that isn't properly
      secured -- whether that's 0, 1, or 2 bolts tight, or no fishplate at
      all -- leaves more energy sitting in the slow ~39 Hz beat, so the
      ratio comes out higher.

  Checked against every "Accurate Readings" file we have: every 3-4 bolt
  (tight) reading scored below 0.30, and every not-secure reading (0-2
  bolts, or no fishplate) scored above 0.38. THRESHOLD below is set to 0.35,
  right in the middle of that gap, with room to spare on both sides.

  If more readings get collected later and that gap narrows or shifts,
  THRESHOLD is the one number to come back and re-check.

  One more check this script does: if a file barely shook at all (overall
  vibration RMS below MIN_RMS), there's no real vibration to judge -- e.g.
  a stationary/motor-off reading -- so it gets flagged as "NOT ENOUGH
  VIBRATION" instead of a confident TIGHT/LOOSE guess. Every real vibrating
  reading in our data scored above ~6,000 RMS; a stationary one scored
  around 36. MIN_RMS sits well below the real readings and well above the
  stationary noise floor, so it won't accidentally skip a real one.

USAGE (same pattern as fft_analysis.py -- run from inside the readings
folder, pointing at this script wherever it lives):

    python classify_tightness.py capture_4vibrating1.csv
    python classify_tightness.py capture_*vibrating*.csv
    python classify_tightness.py capture_*vibrating*.csv --save verdicts.csv

This script needs fft_analysis.py to sit in the same folder as this file --
it reuses that script's loading, FFT, and ratio code rather than repeating it.
"""

import sys
import numpy as np
import pandas as pd

from fft_analysis import load_and_trim, run_fft, expand_args, low_high_ratio

# The line between tight and loose. Based on real data: every tight (3-4
# bolt) reading scored below 0.30, every not-secure reading (0-2 bolts, or
# no fishplate) scored above 0.38 -- 0.35 sits in the middle of that gap.
THRESHOLD = 0.35

# Below this overall vibration strength, there's no real signal to judge --
# treat it as a non-reading rather than guessing LOOSE or TIGHT.
MIN_RMS = 1000


def classify_file(path):
    mag, t_start, t_end, total_rows = load_and_trim(path)
    freqs, amp, mag_c = run_fft(mag)

    rms = float(np.sqrt(np.mean(mag_c**2)))
    ratio = low_high_ratio(freqs, amp)

    if rms < MIN_RMS:
        verdict = "NOT ENOUGH VIBRATION"
        print(
            f"{path:30s}  rms = {rms:7.1f}  ratio = {ratio:7.3f}   ->   "
            f"{verdict} (doesn't look like a real vibrating reading -- skipped)"
        )
    else:
        verdict = "TIGHT" if ratio < THRESHOLD else "LOOSE"
        print(f"{path:30s}  rms = {rms:7.1f}  ratio = {ratio:7.3f}   ->   {verdict}")

    return {
        "file": path,
        "rms": round(rms, 1),
        "ratio": round(ratio, 3),
        "verdict": verdict,
    }


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python classify_tightness.py <capture_file.csv> [more_files.csv ...] [--save verdicts.csv]")
        sys.exit(1)

    save_path = None
    if "--save" in args:
        i = args.index("--save")
        save_path = args[i + 1]
        args = args[:i] + args[i + 2:]

    args = expand_args(args)
    if not args:
        print("No matching files found -- nothing to classify.")
        sys.exit(1)

    print(f"Threshold: ratio < {THRESHOLD} -> TIGHT, otherwise -> LOOSE  (needs RMS >= {MIN_RMS} to judge at all)\n")
    results = [classify_file(path) for path in args]

    if save_path:
        pd.DataFrame(results).to_csv(save_path, index=False)
        print(f"\nSaved verdicts to {save_path}")


if __name__ == "__main__":
    main()
