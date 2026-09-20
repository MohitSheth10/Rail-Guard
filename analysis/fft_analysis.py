"""
fft_analysis.py -- Rail-Guard vibration FFT tool

What this does, in order:
  1. Loads one capture CSV (row/seconds/esp32_index/micros/ax/ay/az format).
  2. Removes each axis's static offset (gravity), then combines ax/ay/az into
     a single "how hard is it shaking right now" magnitude signal.
  3. Automatically finds the vibrating segment: some recordings have the motor
     already running from the first sample, others have a stationary lead-in
     or trailing period. This step trims to just the part where the motor is
     actually on, so a quiet lead-in doesn't water down the FFT.
  4. Runs an FFT on that trimmed segment and reports:
       - the dominant frequency (and next few strongest peaks)
       - overall vibration RMS (how hard it's shaking, ignoring frequency)
       - energy split across a handful of frequency bands
  5. If you pass more than one file, it also prints a summary table so you
     can compare readings side by side.

USAGE (from inside the folder with your capture CSVs):

    Single file:
        python fft_analysis.py capture_4vibrating1.csv

    Several specific files:
        python fft_analysis.py capture_0vibrating1.csv capture_4vibrating1.csv

    Every capture in the folder at once (the script expands the wildcard
    itself, so this works the same in PowerShell, cmd.exe, or bash):
        python fft_analysis.py capture_*vibrating*.csv

    Save the summary table to a CSV instead of just printing it:
        python fft_analysis.py capture_*vibrating*.csv --save summary.csv
"""

import glob
import sys
import numpy as np
import pandas as pd

SAMPLE_RATE_HZ = 1000.0

# Onset/offset detection settings
ONSET_WINDOW_S = 0.5        # rolling window size for spotting motor on/off
ONSET_THRESHOLD_MULT = 5.0  # vibration counts as "on" once it's this many
                             # times louder than the quietest 10% of the file

# Frequency bands to report energy in (Hz) -- edit these once we know which
# band actually separates tight from loose.
BANDS = [(0, 10), (10, 30), (30, 60), (60, 100), (100, 200), (200, 500)]

# The two bands the tight/loose ratio compares. A securely tightened joint
# puts most of its shake into the faster ~79 Hz band; anything not properly
# secured leaves more energy in the slower ~39 Hz band. See
# classify_tightness.py for the actual tight/loose call built on this.
RATIO_LOW_BAND = (30, 60)
RATIO_HIGH_BAND = (60, 100)


def load_and_trim(path):
    """Load a capture CSV and return just the vibrating segment's magnitude
    signal, plus the start/end times (seconds) and the file's total row count."""
    df = pd.read_csv(path)
    ax, ay, az = df["ax"].values, df["ay"].values, df["az"].values
    if "seconds" in df.columns:
        t = df["seconds"].values
    else:
        t = np.arange(len(df)) / SAMPLE_RATE_HZ

    # Remove each axis's static offset (gravity component pointing whichever
    # way the sensor happens to be mounted).
    ax_c = ax - np.median(ax)
    ay_c = ay - np.median(ay)
    az_c = az - np.median(az)
    mag = np.sqrt(ax_c**2 + ay_c**2 + az_c**2)

    # Rolling standard deviation = how "shaky" a short window is. Stationary
    # stretches sit flat and low; the instant the motor turns on this jumps
    # and stays high.
    win = max(1, int(ONSET_WINDOW_S * SAMPLE_RATE_HZ))
    roll_std = pd.Series(mag).rolling(win, center=True, min_periods=1).std().values

    baseline = np.nanpercentile(roll_std, 10)
    threshold = baseline * ONSET_THRESHOLD_MULT
    vibrating = roll_std > threshold

    if vibrating.any():
        idx_on = int(np.argmax(vibrating))
        idx_off = len(vibrating) - 1 - int(np.argmax(vibrating[::-1]))
    else:
        # No clear on/off transition found -- treat the whole recording as
        # the vibrating segment (this happens when the motor was already
        # running for the entire capture, which is common in this data set).
        idx_on, idx_off = 0, len(mag) - 1

    trimmed_mag = mag[idx_on : idx_off + 1]
    return trimmed_mag, t[idx_on], t[idx_off], len(df)


def run_fft(mag):
    """Windowed FFT of a (already-trimmed) vibration magnitude signal."""
    mag_c = mag - np.mean(mag)
    n = len(mag_c)
    window = np.hamming(n)
    sig = mag_c * window

    fft_vals = np.fft.rfft(sig)
    freqs = np.fft.rfftfreq(n, d=1 / SAMPLE_RATE_HZ)
    amp = np.abs(fft_vals) * 2 / np.sum(window)
    return freqs, amp, mag_c


def low_high_ratio(freqs, amp):
    """Ratio of vibration energy in the slow ~39 Hz band to the faster
    ~79 Hz band. Checked against every "Accurate Readings" file we have:
    every securely-tightened (3-4 bolt) reading scored below 0.30, and
    every not-secure reading (0-2 bolts, or no fishplate) scored above
    0.38 -- see classify_tightness.py for the actual tight/loose call."""
    low_mask = (freqs >= RATIO_LOW_BAND[0]) & (freqs < RATIO_LOW_BAND[1])
    high_mask = (freqs >= RATIO_HIGH_BAND[0]) & (freqs < RATIO_HIGH_BAND[1])
    low_energy = float(np.sum(amp[low_mask] ** 2))
    high_energy = float(np.sum(amp[high_mask] ** 2))
    return low_energy / high_energy if high_energy > 0 else float("inf")


def top_peaks(freqs, amp, count=5, min_spacing_hz=2.0):
    """Return the strongest distinct peaks, skipping near-duplicates that
    are really just FFT leakage around the same true peak."""
    mask = freqs > 1.0  # ignore the DC / near-0 Hz leakage
    f_use, a_use = freqs[mask], amp[mask]
    order = np.argsort(a_use)[::-1]

    peaks = []
    for i in order:
        f = f_use[i]
        if all(abs(f - pf) > min_spacing_hz for pf, _ in peaks):
            peaks.append((f, a_use[i]))
        if len(peaks) == count:
            break
    return peaks


def analyze_file(path):
    mag, t_start, t_end, total_rows = load_and_trim(path)
    freqs, amp, mag_c = run_fft(mag)
    peaks = top_peaks(freqs, amp)
    rms = float(np.sqrt(np.mean(mag_c**2)))

    print(f"\n=== {path} ===")
    print(f"Total rows in file: {total_rows}")
    print(
        f"Vibrating segment used: {t_start:.2f}s -> {t_end:.2f}s "
        f"({len(mag)} samples, {len(mag)/SAMPLE_RATE_HZ:.1f}s)"
    )
    print(f"Frequency resolution: {SAMPLE_RATE_HZ/len(mag):.4f} Hz\n")

    print("Top frequency peaks (Hz : amplitude):")
    for f, a in peaks:
        print(f"  {f:7.2f} Hz  ->  {a:9.1f}")

    print(f"\nOverall vibration RMS: {rms:.1f}")

    band_energy = {}
    print("\nEnergy by band:")
    for lo, hi in BANDS:
        bmask = (freqs >= lo) & (freqs < hi)
        e = float(np.sum(amp[bmask] ** 2))
        band_energy[f"energy_{lo}_{hi}Hz"] = e
        print(f"  {lo:3d}-{hi:3d} Hz : {e:14.1f}")

    ratio = low_high_ratio(freqs, amp)
    print(f"\nLow/high energy ratio (30-60Hz / 60-100Hz): {ratio:.3f}")

    return {
        "file": path,
        "dominant_hz": round(peaks[0][0], 2) if peaks else None,
        "dominant_amp": round(peaks[0][1], 1) if peaks else None,
        "rms": round(rms, 1),
        "ratio_low_high": round(ratio, 3),
        **{k: round(v, 1) for k, v in band_energy.items()},
    }


def expand_args(args):
    """Expand any wildcard patterns (e.g. capture_*vibrating*.csv) ourselves.
    PowerShell and cmd.exe don't expand '*' for external programs the way
    bash/zsh do -- they pass the literal text through -- so we handle it
    here instead of relying on the shell. A plain filename with no wildcard
    characters is passed through unchanged."""
    expanded = []
    seen = set()
    for a in args:
        if any(ch in a for ch in "*?[]"):
            matches = sorted(glob.glob(a))
            if not matches:
                print(f"Warning: no files matched pattern: {a}")
            for m in matches:
                if m not in seen:
                    expanded.append(m)
                    seen.add(m)
        else:
            if a not in seen:
                expanded.append(a)
                seen.add(a)
    return expanded


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python fft_analysis.py <capture_file.csv> [more_files.csv ...] [--save summary.csv]")
        sys.exit(1)

    save_path = None
    if "--save" in args:
        i = args.index("--save")
        save_path = args[i + 1]
        args = args[:i] + args[i + 2 :]

    args = expand_args(args)
    if not args:
        print("No matching files found -- nothing to analyze.")
        sys.exit(1)

    results = [analyze_file(path) for path in args]

    if len(results) > 1:
        print("\n\n=== Summary across all files ===")
        summary = pd.DataFrame(results)
        print(summary.to_string(index=False))
        if save_path:
            summary.to_csv(save_path, index=False)
            print(f"\nSaved summary table to {save_path}")


if __name__ == "__main__":
    main()
