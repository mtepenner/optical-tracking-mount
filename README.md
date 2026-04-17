# 🔭 Optical Tracking Mount

An edge-deployed hardware and software stack designed to autonomously point and track telescopes or high-speed astronomy cameras at celestial targets. This project features a robust three-tier architecture: a computer vision pipeline for plate solving, a high-performance kinematic controller for motor orchestration, and a modern web dashboard for remote operation.

## 📑 Table of Contents
- [Features](#-features)
- [Architecture & Technologies](#-architecture--technologies)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Features

* **Autonomous Plate Solving:** Analyzes star centroids using OpenCV and compares them against the Tycho-2/Gaia catalogs to determine exact right ascension and declination.
* **Real-Time Ephemeris Engine:** Calculates current satellite (e.g., ISS) positions and converts equatorial coordinates into pan/tilt (Altitude/Azimuth) kinematics.
* **Closed-Loop Motor Control:** Utilizes a PID controller and step generator to send high-frequency pulses to stepper motors, minimizing tracking error.
* **Low-Latency Operator Dashboard:** A React-based web UI offering live WebRTC camera feeds, a digital crosshair, real-time error graphs, and a manual override joystick.
* **Edge Optimized:** Containerized with Docker and optimized for deployment on Raspberry Pi (ARM architecture).

## 🛠️ Architecture & Technologies

The repository is broken down into three primary microservices:

1. **Vision Pipeline (Python / OpenCV):** Handles hardware interfacing with ZWO ASI cameras, noise subtraction, and astrometry.
2. **Tracking Controller (Go):** The core orchestrator managing calculations, kinematic transformations, and direct hardware communication.
3. **Operator Dashboard (React / TypeScript):** The user-facing application for target selection and mount observation.

## 📋 Prerequisites

* Raspberry Pi (Recommended: Pi 4 or higher)
* ZWO ASI high-speed astronomy camera
* Stepper motors and compatible drivers
* Docker and Docker Compose installed on the host machine
* Linux OS (required for custom `udev` USB rules)

## ⚙️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mtepenner/optical-tracking-mount.git
   cd optical-tracking-mount
   ```

2. **Setup USB Access for the Camera:**
   Copy the `udev` rules to ensure the Docker container can communicate directly with your ZWO camera.
   ```bash
   sudo cp infrastructure/udev_rules/*.rules /etc/udev/rules.d/
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

3. **Build and Deploy via Docker Compose:**
   The `infrastructure/docker-compose.pi.yml` file is configured for the Raspberry Pi environment.
   ```bash
   cd infrastructure
   docker compose -f docker-compose.pi.yml up --build -d
   ```

## 💻 Usage

Once the containers are running on your edge device:

1. Navigate to the Operator Dashboard in your web browser (typically `http://<raspberry-pi-ip>:3000`).
2. Verify the live camera feed is streaming via the **Viewfinder HUD**.
3. Use the **Target Selector** to search for a satellite, planet, or deep space object.
4. Monitor the tracking accuracy via the **Error Graphs** and use the **Manual Override** joystick if minor framing adjustments are needed.

## 🤝 Contributing

Contributions are welcome! Please ensure that any additions to the vision or controller pipelines pass the existing CI/CD workflows, specifically the unit tests for star-centroid extraction algorithms (`test-vision.yml`) and ARM binary builds (`build-edge.yml`).

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License. Copyright (c) 2026 Matthew Timothy Erwin Penner. See the `LICENSE` file for more details.
