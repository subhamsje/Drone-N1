# Field Deployment & Certification Roadmap

## PX4 SITL Testing

```bash
# Terminal 1: PX4 SITL
cd PX4-Autopilot && make px4_sitl gazebo

# Terminal 2: Altaria with SITL
cd N1
export PX4_MODE=sitl
python backend/run.py

# Terminal 3: Validation
python altaria_os/validation/run_suite.py
```

**Pass criteria**: validation pass_rate ≥ 70%, recovery triggered on battery/spoof scenarios.

## HITL Validation

1. Pixhawk on test stand (props removed)
2. `PX4_MODE=hitl` serial connection
3. Inject GPS spoof via RF simulator
4. Verify RTL/land within 5s of IMMEDIATE urgency

## Jetson Deployment

```bash
# Build edge image
docker build -f deploy/Dockerfile.backend -t altaria:3.0-jetson .
docker run --runtime nvidia --device /dev/ttyACM0 \
  -e PX4_MODE=live -e TRITON_URL= altaria:3.0-jetson
```

**Checklist**:
- [ ] TensorRT engines built for failure_predictor
- [ ] YOLO FP16 @ ≥15Hz
- [ ] MAVSDK connects within 10s
- [ ] Offline buffer drains on reconnect
- [ ] Kill-switch tested

## Operational Safety Checklist

- [ ] Safety envelope violations logged
- [ ] Audit trail exportable per flight
- [ ] Probabilistic escalation triggers operator alert
- [ ] Fleet meta-learning syncs post-mission
- [ ] No command bypasses envelope gate

## Autonomous Recovery Test Scenarios

| # | Scenario | Expected |
|---|----------|----------|
| 1 | Motor 1 degradation @ t=30s | THRUST_REALLOC or RTL |
| 2 | GPS spoof injection | VIO mode, HOLD/RTL |
| 3 | Battery 15% | RTL mandatory (envelope) |
| 4 | Turbulence > 0.8 | Reduced aggression |
| 5 | Dual camera failure | Thermal pipeline active |

## Certification Roadmap

1. **Stage A**: SITL validation suite automated in CI
2. **Stage B**: HITL fault injection matrix (DO-178C alignment prep)
3. **Stage C**: Field trials 50+ flights, zero uncommanded RTL failures
4. **Stage D**: Operational approval for logistics pilot customer
