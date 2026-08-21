# Production Deployment Guide for Drone-N1 (Altaria OS)

## 1. Prerequisites
- **Target Hardware:** NVIDIA Jetson Orin Nano (8GB) or Jetson AGX Orin.
- **OS:** Ubuntu 22.04 LTS (JetPack 5.1+ / JetPack 6.0).
- **Flight Controller:** Pixhawk 6X / FMUv6X via Hardware UART/USB.

## 2. Docker Setup
Altaria OS modules are containerized for zero-config edge deployment.
1. Install NVIDIA Container Toolkit on Jetson Linux (L4T).
2. Load the base image and start the core stack:
   ```bash
   docker load -i altaria-os-core.tar
   docker-compose -f docker-compose.prod.yml up -d
   ```

## 3. Systemd Watchdog Configuration
To ensure high availability and self-healing, configure the systemd hardware watchdog:
1. Edit `/etc/systemd/system.conf`:
   ```ini
   RuntimeWatchdogSec=10s
   ShutdownWatchdogSec=10min
   ```
2. Enable the safety monitoring daemon:
   ```bash
   sudo systemctl enable altaria-safetyshield.service
   sudo systemctl start altaria-safetyshield.service
   ```

## 4. MAVROS & PX4 SITL Setup
For testing the cognitive loop before physical flight:
1. **PX4 SITL Start:**
   ```bash
   cd /path/to/PX4-Autopilot
   make px4_sitl gazebo-classic
   ```
2. **MAVROS Connection:**
   Update the connection URL in `mavros_node.launch`:
   ```xml
   <arg name="fcu_url" default="udp://:14540@localhost:14557" />
   ```
3. Launch MAVROS to bridge the Altaria OS with the SITL environment:
   ```bash
   roslaunch altaria_core mavros_sitl.launch
   ```
