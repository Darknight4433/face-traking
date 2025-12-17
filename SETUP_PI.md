
# Human Tracking on Raspberry Pi 4 setup

This project uses **MediaPipe** for face detection and **GPIOZero** for servo control.

## Prerequisites

1.  **Raspberry Pi 4** running Raspberry Pi OS (Legacy "Buster" or "Bullseye" recommended for best camera compatibility, but "Bookworm" works with some tweaks).
2.  **USB Camera** or **Pi Camera Module**.
3.  **2 x Servos** (e.g., SG90) connected to GPIO pins.

## Hardware Connections

- **Pan Servo (Horizontal)**: Pin `GPIO 17` (Physical Pin 11)
- **Tilt Servo (Vertical)**: Pin `GPIO 27` (Physical Pin 13)
- **Power**: Connect Servo VCC to 5V and GND to GND.
- **Damping**: If servos are jittery, connect an external 5V power supply (don't power high-torque servos directly from Pi headers).

## Installation

Run the following commands on your Raspberry Pi terminal:

1.  **Update System**:
    ```bash
    sudo apt update && sudo apt upgrade -y
    ```

2.  **Install System Dependencies**:
    ```bash
    sudo apt install -y python3-opencv python3-pip libatlas-base-dev
    ```

3.  **Enable Pigpio (Better Servo Control)**:
    It reduces jitter significantly.
    ```bash
    sudo apt install -y pigpio python3-pigpio
    sudo systemctl enable pigpiod
    sudo systemctl start pigpiod
    ```

4.  **Install Python Libraries**:
    ```bash
    pip3 install opencv-python mediapipe-rpi4 gpiozero
    ```
    *Note: If `mediapipe-rpi4` fails, try `pip3 install mediapipe` (official builds now support ARM64).*

## Running the Tracker

1.  Make sure you are in the project folder.
2.  Run the main script:
    ```bash
    python3 main.py
    ```

## Troubleshooting

- **Preview Window Error**: If you are running headless (SSH), you cannot see `cv2.imshow`. Comment out `cv2.imshow` and `cv2.waitKey` lines in `main.py`.
- **Servo Jitter**: Ensure `pigpiod` is running (`sudo systemctl start pigpiod`).
- **Camera not found**: Run `libcamera-hello` to test camera (if Pi Cam). You might need to disable legacy camera usage or use `libcamerasrc` in OpenCV if using newer OS versions. For USB cams, it usually works out of the box.

