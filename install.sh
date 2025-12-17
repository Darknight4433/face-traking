#!/bin/bash

echo "Starting installation for Human Tracking on Pi 4..."

# 1. System Updates and Dependencies (non-Python)
echo "Updating system and installing system libraries..."
sudo apt update
sudo apt install -y python3-opencv libatlas-base-dev pigpio python3-pip

# 2. Enable pigpio daemon (for smooth servo control)
echo "Enabling and starting pigpiod..."
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

# 3. Upgrade pip (Crucial for finding wheels)
echo "Upgrading pip..."
pip3 install --upgrade pip

# 4. Install General Python Dependencies
echo "Installing general Python libraries..."
pip3 install -r requirements.txt

# 5. Install MediaPipe (The tricky part on Pi)
echo "Attempting to install MediaPipe..."

# Strategy A: Try the specific Pi 4 community build
if pip3 install mediapipe-rpi4; then
    echo "Success: Installed mediapipe-rpi4"
# Strategy B: Try the official package (works on 64-bit Pi OS)
elif pip3 install mediapipe; then
    echo "Success: Installed official mediapipe"
# Strategy C: Try the rpi3 version (sometimes compatible)
elif pip3 install mediapipe-rpi3; then
    echo "Success: Installed mediapipe-rpi3"
else
    echo "-------------------------------------------------------------"
    echo "ERROR: Could not install 'mediapipe' automatically."
    echo "This is common on Raspberry Pi (especially 32-bit OS)."
    echo ""
    echo "Try installing manually by downloading a wheel (.whl) from:"
    echo "https://pypi.org/project/mediapipe-rpi4/#files"
    echo "or searching 'mediapipe raspberry pi wheel' for your Python version."
    echo "-------------------------------------------------------------"
fi

echo "Installation setup finished!"
