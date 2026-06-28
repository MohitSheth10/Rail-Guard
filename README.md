# 🛡️ Rail-Guard

**IoT-based railway fishplate integrity monitoring system**

> Fishplates are the metal joints connecting two rails. When they crack or loosen, trains derail. Rail-Guard detects this — before it happens.

---

## 📌 What It Does

Rail-Guard is a self-contained embedded device that mounts on a railway fishplate and continuously monitors its structural health. It detects:

- **Vibration anomalies** using two MPU6050 IMUs (accelerometer + gyroscope)
- **Mechanical stress / loosening** using an HX711 load cell amplifier
- **All sensor data is logged** to a micro SD card with timestamps for later ML analysis

When an anomaly is detected, the system flags it. The goal is predictive maintenance — catching failures before they become disasters.

---

## 🔧 Hardware

| Component | Role |
|-----------|------|
| ESP32-S3 Zero | Main microcontroller (Wi-Fi + Bluetooth capable) |
| MPU6050 × 2 | Dual IMUs for vibration & orientation sensing |
| HX711 | Load cell amplifier for stress measurement |
| Micro SD Card Module | On-device data logging |
| L298N Motor Driver | Controls alert/response motors |
| XY-3606 Buck Converter | Steps 12V down to 5V for logic |
| Custom PCB (perfboard) | Hand-assembled circuit board |

### GPIO Pin Map (ESP32-S3 Zero)

| GPIO | Connected To |
|------|-------------|
| GPIO 2 | L298N ENA + ENB (PWM speed) |
| GPIO 3 | L298N IN1 + IN3 (direction) |
| GPIO 4 | HX711 DT |
| GPIO 5 | HX711 SCK |
| GPIO 6 | MPU2 SDA |
| GPIO 7 | MPU2 SCL |
| GPIO 8 | MPU1 SDA |
| GPIO 9 | MPU1 SCL |
| GPIO 10 | SD Card CS |
| GPIO 11 | SD Card MOSI |
| GPIO 12 | SD Card SCK |
| GPIO 13 | SD Card MISO |

---

## 📁 Repository Structure

```
Rail-Guard/
├── docs/
│   ├── Final_Project_Report.pdf     # Full IBDP project report
│   └── Project_LogBook.pdf          # Complete development logbook
├── hardware/
│   ├── schematic/                   # Circuit schematics (as-built)
│   ├── bom/                         # Bill of Materials
│   └── block_diagram/               # System block diagram
├── code/                            # ESP32 firmware
├── media/                           # Photos and demo videos
├── presentations/                   # Pitch deck
└── specification_sheets/            # Component datasheets
```

---

## 🎥 Demo

See the `/media` folder for photos and videos of the assembled device.

---

## 🧠 Machine Learning (Next Phase)

SD-logged sensor data will be used to train a classifier to distinguish:
- Normal train passage vibration
- Loose fishplate signature
- Cracked fishplate signature

---

## 📚 Context

Developed as the **IB Diploma Programme (IBDP) Personal Project**.
Built entirely independently — hardware assembly, circuit design, firmware, and documentation.

**Developer:** Mohit Sheth | **Year:** 2025–2026 | **Status:** Hardware complete. Firmware in development.

---
*Repository is currently private. Will be made public upon project completion.*