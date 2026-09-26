"""
liveclassifytightness.py -- Rail-Guard LIVE tight/loose monitor

This is the real-time version of classify_tightness.py. Instead of reading
a finished capture CSV, it connects straight to the ESP32 over the same USB
cable Arduino uses, reads the ax,ay,az stream as it comes in, and shows a
small window on screen that constantly updates with:

    - TIGHT / LOOSE (big colored text)
    - the bolt-count estimate (e.g. "1 bolt tight (3 loose)")
    - the numbers behind that call (ratio, overall vibration strength)

It reuses the exact same tuned numbers as the rest of the project -- the
0.35 tight/loose threshold, the MIN_RMS cutoff, and the bolt-count
boundaries all come directly from fft_analysis.py and classify_tightness.py
sitting in this same folder. Nothing about the tuning is duplicated or
guessed here -- if those two files ever get re-tuned with more data, this
script picks up the new numbers automatically.

HOW IT WORKS, IN PLAIN TERMS:
    The ESP32 sends one line per sample, 1000 times a second (that's the
    "sample_index,micros,ax,ay,az" format from mpu6050_1khz_stream.ino).
    This script keeps the most recent 2 seconds of samples in memory (a
    rolling window), and twice a second it runs the same FFT math the rest
    of the project uses on whatever is currently in that window, and
    updates the screen with the result. So the display is always showing
    "the last ~2 seconds," updated live.

BEFORE YOU RUN THIS:
    1. Close the Arduino Serial Monitor if it's open. Only one program can
       listen to the USB cable at a time -- this script takes over that
       job, so the Serial Monitor has to let go of it first.
    2. Make sure the ESP32 is running mpu6050_1khz_stream.ino (or any
       sketch that prints the same "sample_index,micros,ax,ay,az" lines at
       1000 Hz). If it's running something else, this will just sit on
       "Waiting for data."
    3. One-time setup, if you haven't already:
           pip install pyserial

HOW TO RUN IT:
    python liveclassifytightness.py

    A window opens. Pick your ESP32's COM port from the dropdown (it's the
    same port Arduino's Tools > Port menu shows) and click Connect.
"""

import queue
import threading
import tkinter as tk
from collections import deque
from tkinter import ttk

import numpy as np
import serial
import serial.tools.list_ports

from fft_analysis import SAMPLE_RATE_HZ, run_fft, low_high_ratio
from classify_tightness import THRESHOLD, MIN_RMS, estimate_bolts_tight

BAUD_RATE = 115200

# How much recent history to judge each update on, and how often to update.
WINDOW_SECONDS = 2.0
WINDOW_SAMPLES = int(WINDOW_SECONDS * SAMPLE_RATE_HZ)
UPDATE_INTERVAL_MS = 500

COLOR_TIGHT = "#1a7a1a"
COLOR_LOOSE = "#b3261e"
COLOR_WAITING = "#8a8a8a"
COLOR_NO_VIBRATION = "#c07a10"


# --------------------------------------------------------------------------
# Core classification -- no serial, no GUI, so it can be tested on its own.
# --------------------------------------------------------------------------

def classify_window(samples):
    """samples: a list of (ax, ay, az) tuples, oldest first.

    Returns a dict describing what to show on screen. This is the live
    equivalent of classify_tightness.classify_file() -- same math, same
    tuned constants, just run on a rolling window instead of a whole file.
    """
    if len(samples) < WINDOW_SAMPLES:
        return {"status": "waiting", "n": len(samples)}

    arr = np.array(samples[-WINDOW_SAMPLES:], dtype=float)
    ax, ay, az = arr[:, 0], arr[:, 1], arr[:, 2]

    ax_c = ax - np.median(ax)
    ay_c = ay - np.median(ay)
    az_c = az - np.median(az)
    mag = np.sqrt(ax_c**2 + ay_c**2 + az_c**2)

    freqs, amp, mag_c = run_fft(mag)
    rms = float(np.sqrt(np.mean(mag_c**2)))
    ratio = low_high_ratio(freqs, amp)

    if rms < MIN_RMS:
        return {"status": "no_vibration", "rms": rms, "ratio": ratio}

    verdict = "TIGHT" if ratio < THRESHOLD else "LOOSE"
    bolt_estimate = estimate_bolts_tight(ratio)
    return {
        "status": "ok",
        "rms": rms,
        "ratio": ratio,
        "verdict": verdict,
        "bolt_estimate": bolt_estimate,
    }


def parse_line(line):
    """Turn one line of serial text into an (ax, ay, az) tuple, or None if
    the line isn't a real data line (header, blank, or a '# rate check' /
    '[FATAL]' status line -- those get skipped, same as daq.py does)."""
    line = line.strip()
    if not line or line.startswith("#") or line.startswith("["):
        return None
    parts = line.split(",")
    if len(parts) != 5:
        return None
    try:
        ax = int(parts[2])
        ay = int(parts[3])
        az = int(parts[4])
    except ValueError:
        return None
    return ax, ay, az


# --------------------------------------------------------------------------
# Serial reading -- runs in a background thread so the GUI never freezes
# waiting on the USB cable.
# --------------------------------------------------------------------------

class SerialReader(threading.Thread):
    def __init__(self, port, buffer, buffer_lock, status_queue):
        super().__init__(daemon=True)
        self.port = port
        self.buffer = buffer
        self.buffer_lock = buffer_lock
        self.status_queue = status_queue
        self.stop_event = threading.Event()
        self.ser = None

    def run(self):
        try:
            self.ser = serial.Serial(self.port, BAUD_RATE, timeout=1)
        except Exception as e:
            self.status_queue.put(("error", str(e)))
            return

        self.status_queue.put(("connected", None))
        while not self.stop_event.is_set():
            try:
                raw = self.ser.readline()
            except Exception as e:
                self.status_queue.put(("error", str(e)))
                break
            if not raw:
                continue
            parsed = parse_line(raw.decode("utf-8", errors="ignore"))
            if parsed is None:
                continue
            with self.buffer_lock:
                self.buffer.append(parsed)

        try:
            self.ser.close()
        except Exception:
            pass
        self.status_queue.put(("disconnected", None))

    def stop(self):
        self.stop_event.set()


# --------------------------------------------------------------------------
# GUI
# --------------------------------------------------------------------------

class LiveClassifyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rail-Guard -- Live Tightness Monitor")
        self.root.geometry("480x360")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.buffer = deque(maxlen=WINDOW_SAMPLES)
        self.buffer_lock = threading.Lock()
        self.status_queue = queue.Queue()
        self.reader = None

        self._build_widgets()
        self._refresh_ports()
        self.root.after(UPDATE_INTERVAL_MS, self._tick)

    def _build_widgets(self):
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Port:").pack(side="left")
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(top, textvariable=self.port_var, width=18, state="readonly")
        self.port_combo.pack(side="left", padx=5)

        ttk.Button(top, text="Refresh", command=self._refresh_ports).pack(side="left", padx=5)
        self.connect_btn = ttk.Button(top, text="Connect", command=self._toggle_connect)
        self.connect_btn.pack(side="left", padx=5)

        self.conn_status_var = tk.StringVar(value="Not connected")
        ttk.Label(top, textvariable=self.conn_status_var).pack(side="left", padx=10)

        # Big verdict
        self.verdict_var = tk.StringVar(value="--")
        self.verdict_label = tk.Label(
            self.root, textvariable=self.verdict_var,
            font=("Segoe UI", 40, "bold"), fg=COLOR_WAITING,
        )
        self.verdict_label.pack(pady=(20, 5))

        self.bolt_var = tk.StringVar(value="")
        ttk.Label(self.root, textvariable=self.bolt_var, font=("Segoe UI", 14)).pack(pady=(0, 15))

        # Small detail numbers
        detail = ttk.Frame(self.root, padding=10)
        detail.pack(fill="x")
        self.detail_var = tk.StringVar(value="Waiting for data...")
        ttk.Label(detail, textvariable=self.detail_var, font=("Segoe UI", 10)).pack()

    def _refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo["values"] = ports
        if ports and not self.port_var.get():
            self.port_var.set(ports[0])

    def _toggle_connect(self):
        if self.reader is not None:
            self._disconnect()
        else:
            self._connect()

    def _connect(self):
        port = self.port_var.get()
        if not port:
            self.conn_status_var.set("Pick a port first")
            return
        self.buffer.clear()
        self.reader = SerialReader(port, self.buffer, self.buffer_lock, self.status_queue)
        self.reader.start()
        self.connect_btn.config(text="Disconnect")
        self.conn_status_var.set(f"Connecting to {port}...")

    def _disconnect(self):
        if self.reader is not None:
            self.reader.stop()
            self.reader = None
        self.connect_btn.config(text="Connect")
        self.conn_status_var.set("Not connected")
        self.verdict_var.set("--")
        self.verdict_label.config(fg=COLOR_WAITING)
        self.bolt_var.set("")
        self.detail_var.set("Waiting for data...")

    def _tick(self):
        # Drain any connection status updates
        try:
            while True:
                kind, info = self.status_queue.get_nowait()
                if kind == "connected":
                    self.conn_status_var.set(f"Connected to {self.port_var.get()}")
                elif kind == "error":
                    self.conn_status_var.set(f"Error: {info}")
                    self.reader = None
                    self.connect_btn.config(text="Connect")
                elif kind == "disconnected":
                    if self.conn_status_var.get().startswith("Connected"):
                        self.conn_status_var.set("Disconnected")
        except queue.Empty:
            pass

        with self.buffer_lock:
            samples = list(self.buffer)

        result = classify_window(samples)
        self._update_display(result)

        self.root.after(UPDATE_INTERVAL_MS, self._tick)

    def _update_display(self, result):
        status = result["status"]

        if status == "waiting":
            secs = result["n"] / SAMPLE_RATE_HZ
            self.verdict_var.set("Warming up...")
            self.verdict_label.config(fg=COLOR_WAITING)
            self.bolt_var.set("")
            self.detail_var.set(
                f"Buffering: {result['n']}/{WINDOW_SAMPLES} samples ({secs:.1f}s / {WINDOW_SECONDS:.0f}s needed)"
            )
        elif status == "no_vibration":
            self.verdict_var.set("NOT ENOUGH VIBRATION")
            self.verdict_label.config(fg=COLOR_NO_VIBRATION)
            self.bolt_var.set("(motor may be off, or nothing is shaking right now)")
            self.detail_var.set(f"rms = {result['rms']:.1f}   ratio = {result['ratio']:.3f}")
        else:  # ok
            verdict = result["verdict"]
            self.verdict_var.set(verdict)
            self.verdict_label.config(fg=COLOR_TIGHT if verdict == "TIGHT" else COLOR_LOOSE)
            self.bolt_var.set(f"Bolt-count estimate (experimental): {result['bolt_estimate']}")
            self.detail_var.set(
                f"rms = {result['rms']:.1f}   ratio = {result['ratio']:.3f}   "
                f"(threshold: ratio < {THRESHOLD} = TIGHT)"
            )

    def on_close(self):
        if self.reader is not None:
            self.reader.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    LiveClassifyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
