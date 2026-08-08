# Altaria OS — Enterprise Deployment & Production Operations Guide

This guide provides comprehensive instructions for deploying Altaria OS in commercial cloud, on-premise defense data centers, and embedded Jetson edge hardware.

---

## 🐳 1-Click Multi-Container Deployment

Deploy the entire microservice stack with Docker Compose:

```bash
docker compose up -d
```

### Stack Components:
- **FastAPI Sovereign Kernel (`altaria-backend`)**: Port `8080`
- **Planetary Command Surface UI (`altaria-frontend`)**: Port `5173` (Nginx static bundle)
- **ClickHouse Telemetry Lakehouse (`clickhouse`)**: Ports `8123` (HTTP) & `9000` (Native)
- **PX4 Headless SITL Simulator (`px4-sitl`)**: UDP Port `14540`

---

## 🐍 Local Bare-Metal Development Setup

### 1. Backend Startup:
```bash
source venv/bin/activate
PYTHONPATH=. python backend/run.py
```
*API runs at `http://localhost:8080` with interactive Swagger docs at `/docs`.*

### 2. Frontend Startup:
```bash
cd frontend/apps/command
npm install
npm run dev
```
*Command Surface launches at `http://localhost:5173`.*

---

## 🧪 Automated Validation Suite
Execute the 6-scenario empirical flight validation test campaign:
```bash
source venv/bin/activate
python validation/run_all_validation_campaigns.py
```
*Outputs JSON evidence to `validation/reports/empirical_validation_evidence.json`.*
