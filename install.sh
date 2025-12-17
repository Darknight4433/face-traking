#!/bin/bash

echo "Starting installation for Human Tracking on Pi 4..."

# 1. System Updates and Dependencies (non-Python)
echo "Updating system and installing system libraries..."
sudo apt update
sudo apt install -y python3-opencv libatlas-base-dev pigpio

# 2. Enable pigpio daemon (for smooth servo control)
echo "Enabling and starting pigpiod..."
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

# 3. Python Dependencies
echo "Installing Python libraries..."
# Try specific Pi 4 optimized mediapipe first, else fallback to standard
pip3 install mediapipe-rpi4 2>/dev/null || pip3 install mediapipe
pip3 install -r requirements.txt

echo "Installation complete! Run 'python3 main.py' to start."
