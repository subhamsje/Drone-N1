# System Architecture Specification for Drone-N1 (Altaria OS)

## 1. 8-Subsystem Stack
The Altaria OS consists of 8 distinct subsystems (D0 through D7) managed by a strict deterministic scheduler. This scheduler ensures temporal isolation and predictable execution for all real-time tasks, bounding the worst-case execution time (WCET) for safety-critical components.

```mermaid
graph TD
    Scheduler[D0-D7 Deterministic Scheduler]
    D0[D0: Flight Control & Stability]
    D1[D1: AFKF Sensor Fusion]
    D2[D2: Motor Mixing & Actuation]
    D3[D3: Vision & Obstacle Avoidance]
    D4[D4: Path Planning & Nav]
    D5[D5: Telemetry & Comm]
    D6[D6: Payload Management]
    D7[D7: System Diagnostics]
    
    Scheduler -->|1000Hz| D0
    Scheduler -->|1000Hz| D1
    Scheduler -->|500Hz| D2
    Scheduler -->|60Hz| D3
    Scheduler -->|10Hz| D4
    Scheduler -->|50Hz| D5
    Scheduler -->|10Hz| D6
    Scheduler -->|1Hz| D7
```

## 2. Cognitive Loop & Autonomy
The cognitive loop manages high-level autonomy, fusing perception data into actionable waypoints and velocity commands. This loop operates asynchronously from the core flight control to prevent computational bottlenecks.

```mermaid
flowchart LR
    Sensors[(Sensors: Lidar/Camera/Radar)] --> PreProcessing[Data Pre-processing]
    PreProcessing --> Perception[Perception Module]
    Perception --> Mapping[Local Mapping / Voxel Grid]
    Mapping --> Planning[Path Planning / Trajectory Gen]
    Planning --> Validation[Trajectory Validation]
    Validation --> Control[Flight Control]
    Control --> Actuators((Actuators))
```

## 3. Fail-Safe Recovery Flow
The Safety Shield continuously monitors system invariants. In the event of a critical subsystem failure, it overrides standard operations. It maintains strict DAL-A compliance by executing on a verified isolated partition.

```mermaid
stateDiagram-v2
    [*] --> NormalOperation
    NormalOperation --> AnomalyDetected : Threshold Exceeded
    AnomalyDetected --> SafetyShieldEvaluation : Trigger Alert
    SafetyShieldEvaluation --> NormalOperation : False Alarm
    SafetyShieldEvaluation --> DegradedMode : Minor Sensor Fault
    DegradedMode --> NormalOperation : Fault Cleared
    SafetyShieldEvaluation --> EmergencyRTL : GPS Available & Link Active
    SafetyShieldEvaluation --> ImmediateLanding : GPS Lost / Critical Failure
    EmergencyRTL --> Grounded
    ImmediateLanding --> Grounded
    Grounded --> [*]
```

## 4. Hardware Interaction & Memory Model
Memory allocation in Altaria OS is strictly static. No dynamic memory allocation (`malloc`, `free`) is permitted after system initialization to prevent memory fragmentation and out-of-memory errors during runtime.

```mermaid
graph LR
    HW[Hardware Layer] <--> HAL[Hardware Abstraction Layer]
    HAL <--> CoreOS[Altaria OS Core]
    CoreOS --> StaticMem[Static Memory Pools]
    CoreOS --> Tasks[Task Handlers]
```
