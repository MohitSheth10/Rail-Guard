"""
daq.py  -  Rail-Guard serial data logger

Reads the vibration stream from the ESP32-S3 over USB serial and saves it to a
timestamped CSV file. Records continuously until you press Ctrl+C.

Line format expected from the ESP32 (comma-separated integers), e.g.:
    1498,1497999,4039,212,-836
      |    |       |    |    |
      |    |       +----+----+--- accelerometer X, Y, Z (raw counts)
      |    +------------------- micros() timestamp on the ESP32
      +------------------------ ESP32's own sample counter

~1000 lines/second expected. If a second MPU is streamed, each line has 8 fields
(index, micros, ax1, ay1, az1, ax2, ay2, az2); the column count is auto-detected.

The CSV this script writes adds two of its OWN columns in front - 'row' (starts
at 1) and 'seconds' - both fresh for THIS file. Use those for plotting. The
ESP32's own 'esp32_index'/'micros' columns are kept too (useful for
gap-checking) but they keep counting from whenever the board last rebooted, not
from when this script started - so if you reconnect mid-stream without
resetting the board, those two can start at a large number. That's expected,
not an error.

WHILE RECORDING, this script watches the ESP32's own micros() timestamps (the
authoritative measure of real sample timing - not Python's wall clock, which
has its own OS/USB jitter) and will:
  - immediately print a STALL warning if any single gap between samples is
    bigger than STALL_THRESHOLD_US (default 1.5 ms) - this is what a broken /
    un-rate-limited firmware looks like, and you'll see it as it happens
    instead of finding out after the fact from the CSV.
  - print a rate WARNING every RATE_CHECK_ROWS rows if the achieved rate is
    off TARGET_RATE_HZ by more than RATE_WARN_PCT.

USAGE (from the Values folder):
    venv\\Scripts\\python.exe daq.py

Press Ctrl+C to stop; the CSV is flushed and closed cleanly.
"""

import csv
import sys
import time
from datetime import datetime

import serial  # pyserial


# ============================ EDIT THESE ================================== #
PORT = "COM13"          # <-- set your ESP32's COM port here
BAUD = 115200           # ignored by native USB CDC, but harmless to set
OUTFILE = None          # None = auto name capture_YYYYMMDD_HHMMSS.csv,
                        # or set e.g. "my_run.csv"
DISPLAY_HZ = 10         # how many times/second to refresh the live on-screen view
                        # (the CSV still records EVERY row - this only limits the
                        # screen updates so printing doesn't slow down reading)

TARGET_RATE_HZ      = 1000   # expected sample rate, matches the ESP32 sketch
STALL_THRESHOLD_US  = 1500   # a single gap bigger than this = flagged immediately
RATE_CHECK_ROWS     = 1000   # re-check the achieved rate every N rows
RATE_WARN_PCT       = 5.0    # warn if the windowed rate is off target by more than this
# ========================================================================= #


def is_data_line(fields):
    """True only if EVERY field is a plain integer, so we skip headers, markers
    and the timing-report text the sketch may also print."""
    if len(fields) < 3:
        return False
    for f in fields:
        if not f.strip().lstrip("-").isdigit():
            return False
    return True


def build_header(n_cols):
    """Name the columns based on how many arrived.

    'row' and 'seconds' are added by THIS script, fresh per file (0-based) -
    they are NOT the same as the ESP32's own counters. The ESP32's sample
    counter and micros() keep running from whenever the board last actually
    rebooted, not from when this script started listening, so a mid-stream
    reconnect can start at a large number (e.g. 291517) - that's expected,
    not an error. Plot against 'seconds', not 'esp32_index', to avoid that
    confusion in charts.
    """
    if n_cols == 5:                       # index, micros, 1 MPU
        return ["row", "seconds", "esp32_index", "micros", "ax", "ay", "az"]
    if n_cols == 8:                       # index, micros, 2 MPUs
        return ["row", "seconds", "esp32_index", "micros",
                "ax1", "ay1", "az1", "ax2", "ay2", "az2"]
    return ["row", "seconds", "esp32_index", "micros"] + [f"v{i}" for i in range(n_cols - 2)]


def main():
    out_path = OUTFILE or f"capture_{datetime.now():%Y%m%d_%H%M%S}.csv"

    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
    except serial.SerialException as e:
        print(f"ERROR: could not open {PORT}: {e}")
        print("Tips: close the Arduino Serial Monitor (it locks the port), and "
              "check the port in Arduino IDE > Tools > Port.")
        sys.exit(1)

    print(f"Listening on {PORT} @ {BAUD} baud")
    print(f"Writing to   {out_path}")
    print("Recording... press Ctrl+C to stop.\n")

    header = None
    count = 0                      # rows written so far
    t_start = None
    first_micros = None            # ESP32 micros() of this file's first row
    prev_micros = None             # ESP32 micros() of the previous row (for stall check)
    f = open(out_path, "w", newline="")
    writer = csv.writer(f)

    display_period = 1.0 / DISPLAY_HZ
    last_display = 0.0
    last_flush = 0

    stall_count = 0
    window_start_micros = None     # start of the current rate-check window
    window_start_count = 0

    try:
        while True:                              # runs until Ctrl+C
            raw = ser.readline()
            if not raw:
                continue                          # timeout, no data this tick
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue

            fields = line.split(",")
            if not is_data_line(fields):
                # non-data line (banner / report): print on its own line so it
                # doesn't collide with the live status line
                print(f"\n  [info] {line}")
                continue

            esp_micros = int(fields[1])

            if header is None:                    # first real row
                header = build_header(len(fields))
                writer.writerow(header)
                n_mpu = (len(fields) - 2) // 3
                print(f"Detected {len(fields)} columns "
                      f"({n_mpu} MPU{'s' if n_mpu != 1 else ''}). "
                      f"Header: {','.join(header)}\n")
                t_start = time.time()
                first_micros = esp_micros
                prev_micros = esp_micros
                window_start_micros = esp_micros
                window_start_count = 0

            # this file's own row number (1-based) and elapsed seconds, so
            # charts never get confused by the ESP32's running (non-reset)
            # counters
            count += 1
            seconds = (esp_micros - first_micros) / 1_000_000.0
            writer.writerow([count, f"{seconds:.6f}"] + fields)   # EVERY row is saved

            # ---- immediate stall check, using the ESP32's own timestamps ----
            gap_us = esp_micros - prev_micros
            if gap_us > STALL_THRESHOLD_US:
                stall_count += 1
                print(f"\n  !! STALL: {gap_us/1000:.1f} ms gap at row {count} "
                      f"(t={seconds:.3f}s) - firmware may not be rate-limited")
            prev_micros = esp_micros

            # ---- periodic rate check, using the ESP32's own timestamps ----
            rows_in_window = count - window_start_count
            if rows_in_window >= RATE_CHECK_ROWS:
                window_us = esp_micros - window_start_micros
                rate_hz = rows_in_window * 1_000_000.0 / window_us if window_us > 0 else 0.0
                err_pct = abs(rate_hz - TARGET_RATE_HZ) / TARGET_RATE_HZ * 100.0
                if err_pct > RATE_WARN_PCT:
                    print(f"\n  !! RATE WARNING: {rate_hz:.0f} Hz "
                          f"({err_pct:.1f}% off target {TARGET_RATE_HZ} Hz) "
                          f"at row {count} - check the firmware / re-upload")
                window_start_micros = esp_micros
                window_start_count = count

            # ---- live on-screen view (throttled to DISPLAY_HZ) ----
            now = time.time()
            if now - last_display >= display_period:
                last_display = now
                elapsed = now - t_start
                rate = count / elapsed if elapsed > 0 else 0.0
                # show index/micros + all axis values from the latest row
                idx = fields[0]
                axes = " ".join(f"{v:>7}" for v in fields[2:])
                # \r rewrites the SAME line in place -> a live-updating readout
                print(f"\r rows:{count:>8}  {rate:>4.0f}/s  stalls:{stall_count:>3}  |  "
                      f"idx {idx:>8}  [{axes} ]   ",
                      end="", flush=True)

            # flush the file to disk about once a second (independent of display)
            if count - last_flush >= 1000:
                last_flush = count
                f.flush()

    except KeyboardInterrupt:
        print("\nStopped by user (Ctrl+C).")
    finally:
        f.flush()
        f.close()
        ser.close()
        if t_start and count:
            elapsed = time.time() - t_start
            rate = count / elapsed if elapsed > 0 else 0.0
            print(f"\nSaved {count} rows to {out_path}")
            print(f"Duration {elapsed:.2f} s  ->  {rate:.1f} rows/s (expected ~{TARGET_RATE_HZ})")
            if stall_count == 0:
                print("No timing stalls detected. Looks clean.")
            else:
                print(f"WARNING: {stall_count} timing stall(s) detected during this "
                      f"recording - see the '!! STALL' lines above. This capture "
                      f"is NOT reliable for FFT; fix the firmware and recapture.")
        else:
            print(f"\nNo data rows captured. File: {out_path}")


if __name__ == "__main__":
    main()
