# System Architecture Specification for Drone-N1 (Altaria OS)

## 1. 8-Subsystem Stack
The Altaria OS consists of 8 distinct subsystems (D0 through D7) managed by a strict deterministic scheduler.

```mermaid
graph TD
    Scheduler[D0-D7 Deterministic Scheduler]
    D0[D0: Flight Control]
    D1[D1: AFKF Sensor Fusion]
    D2[D2: Motor Mixing & Actuation]
    D3[D3: Vision & Obstacle Avoidance]
    D4[D4: Path Planning & Nav]
    D5[D5: Telemetry & Comm]
    D6[D6: Payload Management]
    D7[D7: System Diagnostics]
    
    Scheduler --> D0
    Scheduler --> D1
    Scheduler --> D2
    Scheduler --> D3
    Scheduler --> D4
    Scheduler --> D5
    Scheduler --> D6
    Scheduler --> D7
```

## 2. Cognitive Loop
The cognitive loop manages the high-level autonomy, fusing perception data into actionable waypoints and velocity commands.

```mermaid
flowchart LR
    Sensors[(Sensors: Lidar/Camera)] --> Perception[Perception Module]
    Perception --> Mapping[Local Mapping]
    Mapping --> Planning[Path Planning]
    Planning --> Control[Flight Control]
    Control --> Actuators((Actuators))
```

## 3. Fail-Safe Recovery Flow
The Safety Shield continuously monitors the system. In the event of a critical subsystem failure, it overrides standard operations.

```mermaid
stateDiagram-v2
    [*] --> NormalOperation
    NormalOperation --> AnomalyDetected : Threshold Exceeded
    AnomalyDetected --> SafetyShieldEvaluation : Trigger Alert
    SafetyShieldEvaluation --> NormalOperation : False Alarm
    SafetyShieldEvaluation --> EmergencyRTL : GPS Available
    SafetyShieldEvaluation --> ImmediateLanding : GPS Lost / Critical Failure
    EmergencyRTL --> Grounded
    ImmediateLanding --> Grounded
    Grounded --> [*]
```
