# Cassandra Architecture

> **Project Goal**
>
> Cassandra is a behavior-based desktop observation framework. Its purpose is to collect structured evidence about a computer's current state so higher-level systems can reason, automate, or assist users without tightly coupling observation and decision-making.

---

# Current Architecture

```
                Cassandra
                     │
             Sensor Registry
                     │
          Observation Engine
                     │
              Observation Model
                     │
        Structured Observation Data
```

The Observation Engine coordinates independent sensors and produces a standardized Observation object.

Each sensor has a single responsibility and contributes one piece of evidence.

---

# Current Components

```
cassandra/
│
├── about.py
├── __main__.py
│
├── observation/
│   ├── engine.py
│   ├── models.py
│   └── sensors/
│       ├── base.py
│       ├── registry.py
│       ├── time.py
│       └── clipboard.py
│
├── planner/
├── memory/
├── evaluation/
└── environments/
```

---

# Observation Pipeline

```
Application Startup
        │
        ▼
Create Environment
        │
        ▼
Build Sensor Registry
        │
        ▼
Observation Engine
        │
        ▼
Execute Sensors
        │
        ▼
Collect Evidence
        │
        ▼
Create Observation Object
        │
        ▼
Return Structured Data
```

---

# Current Sensors

| Sensor | Purpose | Status |
|---------|---------|--------|
| TimeSensor | Collect UTC timestamp and timezone | ✅ Working |
| ClipboardSensor | Capture clipboard contents | ✅ Working |

---

# Observation Object

Every observation follows the same schema.

```text
Observation
├── environment
├── visual
├── state
├── evidence
├── metadata
├── sensors
├── observation_id
└── timestamp
```

Because the schema is fixed, new sensors can be added without changing the overall structure.

---

# Project Status

| Component | Status |
|----------|--------|
| Framework Architecture | 🚧 In Progress |
| Application Startup | ✅ Working |
| Observation Engine | ✅ Working |
| Observation Model | ✅ Working |
| Sensor Framework | ✅ Working |
| Sensor Registry | ✅ Working |
| Time Sensor | ✅ Working |
| Clipboard Sensor | ✅ Working |
| Window Sensor | 📋 Planned |
| Screenshot Sensor | 📋 Planned |
| OCR Sensor | 📋 Planned |
| State Tracking | 📋 Planned |
| Replay System | 📋 Planned |
| Evaluation Engine | 📋 Planned |
| Planner | 📋 Planned |
| Memory System | 📋 Planned |

---

# Design Principles

Cassandra follows several architectural principles.

## Single Responsibility

Each sensor performs exactly one task.

```
ClipboardSensor
    ↓
Clipboard only
```

---

## Composition over Inheritance

The Observation Engine is composed of sensors rather than implementing sensor logic itself.

```
ObservationEngine
    ├── TimeSensor
    ├── ClipboardSensor
    └── ...
```

---

## Extensibility

Adding a new capability should require:

1. Create a new Sensor.
2. Register it.
3. Run Cassandra.

The Observation Engine should not require modification.

---

# Near-Term Roadmap

## Phase 1 – Observation

- ✅ Time Sensor
- ✅ Clipboard Sensor
- ⬜ Window Sensor
- ⬜ Screenshot Sensor
- ⬜ OCR Sensor

---

## Phase 2 – State Awareness

- Window tracking
- Application context
- State model
- Event history

---

## Phase 3 – Evaluation

- Rule engine
- Goal evaluation
- Task recognition
- Behavior analysis

---

## Phase 4 – Planning

- Action selection
- Planner
- Execution strategies
- Automation hooks

---

# Long-Term Vision

Cassandra is designed as an observation framework.

It answers one fundamental question:

> **What is happening on this computer right now?**

Higher-level systems—including planners, AI agents, automation engines, and research assistants—can build on this structured observation layer without being coupled to the underlying sensors.
