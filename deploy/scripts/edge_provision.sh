#!/bin/bash
# Altaria OS Edge Provisioning Script
# Target: NVIDIA Jetson Orin NX / AGX Orin
# Sets up JetPack, Docker, ROS2, and Altaria Edge Runtime.

set -e

echo "===================================================="
echo "    ALTARIA OS - EDGE HARDWARE PROVISIONING"
echo "===================================================="

# 1. Verify Architecture
ARCH=$(uname -m)
if [ "$ARCH" != "aarch64" ]; then
    echo "[!] CRITICAL: This script must be run on Jetson Orin (aarch64)."
    exit 1
fi

echo "[*] Setting up NVIDIA Jetson container runtime..."
sudo apt-get update
sudo apt-get install -y nvidia-jetpack nvidia-container-runtime docker.io

echo "[*] Configuring Docker for Edge Execution..."
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

echo "[*] Pulling Altaria Edge Image from Registry..."
# In production, this pulls from a secure AWS ECR
docker pull nvcr.io/nvidia/l4t-pytorch:r35.2.1-pth2.0-py3

echo "[*] Building Local Edge Container..."
cd /opt/altaria
docker build -f deploy/Dockerfile.edge -t altaria-edge:latest .

echo "[*] Initializing Edge Autonomy Runtime (Offline Mode)..."
docker run -d \
    --name altaria-kernel \
    --runtime nvidia \
    --network host \
    --restart always \
    -e ALTARIA_EDGE_MODE=1 \
    -e ALTARIA_UAV_ID=$(hostname) \
    --device=/dev/ttyACM0 \
    altaria-edge:latest

echo "===================================================="
echo "[+] SUCCESS: Altaria Edge Runtime is active."
echo "[+] Device is armed for disconnected flight authority."
echo "===================================================="