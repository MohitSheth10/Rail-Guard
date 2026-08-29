# Specification Sheets

Datasheets for the main components used in Rail-Guard.

These are kept here so the hardware choices can be checked against the actual component specifications rather than just the name printed on a module listing.

One useful example is the accelerometer board.

The board was labelled/sold as an MPU-6050/GY-521, but the actual chip identification returned `0x70`, which indicates an MPU-6500 rather than an MPU-6050.

The hardware documentation records this because I checked the chip itself instead of assuming the label was correct.

See [`../docs/04-electronics.md`](../docs/04-electronics.md) for the details.

## Datasheets in this folder

- [`ESP32-S3-Zero-Spec 1.pdf`](ESP32-S3-Zero-Spec%201.pdf) — main controller
- [`mpu-6050 gy-521 Spec Sheet.pdf`](mpu-6050%20gy-521%20Spec%20Sheet.pdf) — accelerometer board (see the note above)
- [`L298N Motor Driver Spec sheet.pdf`](L298N%20Motor%20Driver%20Spec%20sheet.pdf) — motor driver
- [`XY3606 specification sheet.pdf`](XY3606%20specification%20sheet.pdf) — power module
