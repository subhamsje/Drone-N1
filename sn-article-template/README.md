# Drone-N1 (Altaria OS)

> **An Autonomous Aviation Operating System for Mission Intelligence, Digital Twin Simulation, and Fleet-Scale Aerial Operations**  
> *Authored by Subham Sagar Jena & Arathi Sankar P (Dayananda Sagar College of Engineering)*

---

## 📌 Overview

**Drone-N1** is a sovereign, safety-critical autonomous aviation operating system powered by the **Altaria OS** kernel. Sitting directly above standard flight controllers (PX4, ArduPilot), Drone-N1 bridges the gap between low-level motor stabilization and high-level mission intelligence.

### Key Capabilities
* **Mixed-Criticality Real-Time Scheduler**: 8 execution domains ($\mathcal{D}_0 - \mathcal{D}_7$) with an $8.0\,\text{ms}$ hard budget for flight stabilization ($\mathcal{D}_0$).
* **AFKF-SPRT GNSS Spoofing Rejection**: Adaptive Federated Kalman Filter with Sequential Probability Ratio Testing for sub-$15\,\text{ms}$ Visual-Inertial Odometry (VIO) takeover.
* **AI Safety Shield**: Hard real-time MAVLink setpoint interceptor enforcing DO-178C DAL-A safety bounds.
* **20D Digital Twin Sandbox**: 1-millisecond counterfactual physics simulator predicting safety along candidate flight paths.
* **4-Category Risk Engine**: Real-time evaluation of Environmental, Hardware, Cyber/GNSS, and Mission risks.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.9+
- LaTeX distribution (`pdflatex`)

### 2. Run Monte Carlo Simulation Benchmark (200 Trials)
```bash
python3 run_simulation_bench.py
```

### 3. Open Interactive Ground Control Dashboard
```bash
open gcs_dashboard.html
```

### 4. Compile Springer Nature Academic Article
```bash
pdflatex sn-article.tex
```

---

## 📊 Benchmark Summary (200 Monte Carlo Trials)

| Metric | Standard PX4 | AutoGNN | MARL-UAV | **Drone-N1 (Altaria OS)** |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Success Rate** | 69.5% | 86.0% | 88.0% | **96.5% ($p < 0.001$)** |
| **$\mathcal{D}_0$ Critical Latency** | Static | $184.2\,\text{ms}$ | $142.6\,\text{ms}$ | **$0.042\,\text{ms}$** |
| **AFKF Takeover Latency** | Manual RTL | N/A | N/A | **$8.20\,\text{ms}$** |
| **Safety Assurance** | None | Ad-hoc | Ad-hoc | **DO-178C DAL-A** |

---

## 📂 Project Structure

```
sn-article-template/
├── drone_n1/                # Core Altaria OS Kernel Engine
│   ├── altaria_kernel.py    # Cognitive 4-step loop orchestrator
│   ├── afkf_estimator.py    # AFKF-SPRT sensor takeover engine
│   ├── ai_safety_shield.py  # MAVLink safety interceptor
│   ├── digital_twin_sim.py  # 1ms fast-forward physics sandbox
│   └── risk_engine.py       # 4-category operational risk model
├── docs/                    # Technical architecture & DO-178C specs
├── gcs_dashboard.html       # Standalone 3D interactive Web HUD
├── run_simulation_bench.py  # 200-trial Monte Carlo benchmark script
├── sn-article.tex           # Springer Nature LaTeX journal paper
└── sn-article.pdf           # Compiled 10-page research article
```

---

## 🛡️ License & Citation
Copyright (c) 2026 Subham Sagar Jena & Arathi Sankar P. All rights reserved.
