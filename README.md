<p align="center">
  <img src="https://stageonecloudwebmedia.blob.core.windows.net/webdevmedia/cassandra_banner.png" alt="Cassandra Banner" width="100%"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/AI-Local%20LLMs-black?style=flat-square"/>
  <img src="https://img.shields.io/badge/Architecture-Environment%20Agnostic-4CAF50?style=flat-square"/>
  <img src="https://img.shields.io/badge/Status-Early%20Development-orange?style=flat-square"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square"/>
  <img src="https://img.shields.io/badge/built_by-Stage_One_Cloud-7DD3FC?style=flat-square"/>
</p>

---

# Cassandra

Cassandra is an environment-agnostic framework for observing, evaluating, and comparing how language models behave under changing conditions.

Rather than measuring only whether a model completed a task, Cassandra is designed to preserve evidence about how models observe, reason, adapt, and respond as their environment, available context, and quality of information change.

The project began while building **OasisAI**. After repeatedly running into the practical limitations of smaller local language models, the question shifted from:

> **"How do I make the model bigger?"**

to

> **"What can I learn about how the model behaves?"**

That question became Cassandra.

---

# Design Philosophy

Cassandra is built around a simple principle:

**Observe first. Interpret second.**

Instead of treating an LLM like a black box, Cassandra captures evidence that allows experiments to be reviewed, compared, and eventually replayed.

The framework is intended to answer questions such as:

- How does a model respond when context changes?
- Does additional documentation improve performance?
- How does behavior differ between models?
- What happens when tools become unavailable?
- Can smaller local models perform better when the surrounding system improves?

Rather than assuming larger models are always the answer, Cassandra explores how architecture, tooling, and environment influence AI behavior.

---

# Core Architecture

```text
                    ┌─────────────────────────────┐
                    │          CASSANDRA          │
                    │ Behavioral AI Framework     │
                    └──────────────┬──────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   OBSERVATION    │    │    REASONING     │    │    EVALUATION    │
│                  │    │                  │    │                  │
│ • Screenshots    │    │ • Prompts        │    │ • Results        │
│ • Window State   │    │ • Decisions      │    │ • Latency        │
│ • Metadata       │    │ • Tool Usage     │    │ • Retries        │
│ • Sensors        │    │ • Planning       │    │ • Recovery       │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                       │                       │
         └───────────────────────┴───────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │      ENVIRONMENTS      │
                    │                        │
                    │ • The Farmer Was       │
                    │   Replaced             │
                    │ • Market Intelligence  │
                    │ • Desktop Apps         │
                    │ • Browser Automation   │
                    │ • Future Experiments   │
                    └────────────────────────┘
```

---

# Current Experiment

## Experiment 001 — The Farmer Was Replaced

The first Cassandra experiment uses *The Farmer Was Replaced* as a controlled environment.

The objective is **not** to automate a game.

Instead, it provides a repeatable environment where model behavior can be observed, measured, and compared under controlled conditions.

Current work focuses on:

- Window discovery
- Screenshot capture
- Structured observations
- Metadata collection
- Observation logging

Future experiments will introduce planning, memory, deterministic actions, and comparative model evaluation.

---

# Repository Structure

```text
cassandra/
│
├── observation/
├── sensors/
├── planner/
├── evaluation/
├── memory/
├── actions/
│
docs/
│
experiments/
├── the-farmer-was-replaced/
└── future-experiments/
```

---

# Project Status

## Cassandra Development Roadmap

| Phase | Objective | Status | Deliverables |
|-------|-----------|:------:|--------------|
| **Phase 0** | Foundation | ✅ Complete | Application startup, sensor framework, observation engine, observation model |
| **Phase 1** | Perception & Understanding | 🟡 In Progress | Evaluation engine, behavior events, persistent behavior timeline |
| **Phase 2** | Episodic Memory | 🚧 Current Focus | Group behavior events into meaningful work sessions (episodes) |
| **Phase 3** | Semantic Memory | 📋 Planned | Extract long-term knowledge and recurring behavioral patterns |
| **Phase 4** | Environment Interaction | 📋 Planned | Keyboard, mouse, and window interaction APIs |
| **Phase 5** | Closed-Loop Agent | 📋 Planned | Observe → Reason → Act → Observe feedback loop |
| **Phase 6** | Experimental Environments | 📋 Planned | Controlled interaction with *The Farmer Was Replaced* for behavioral research |

| Layer | Purpose | Status |
|--------|---------|:------:|
| Sensors | Capture evidence from the environment | ✅ Complete |
| Observation | Normalize sensor output | ✅ Complete |
| Evaluation | Detect meaningful changes | 🟡 Working |
| Behavior Memory | Record behavioral events over time | 🟡 Working |
| Episodic Memory | Group behaviors into activities | 🚧 In Development |
| Semantic Memory | Learn recurring concepts and patterns | 📋 Planned |
| Interaction Layer | Execute keyboard and mouse actions | 📋 Planned |
| Planning | Select actions based on observations | 📋 Planned |
| Autonomous Agent | Complete closed-loop reasoning | 📋 Planned |

| Stage | Cassandra Capability | Farmer Interaction |
|--------|----------------------|--------------------|
| Stage 1 | Observe | Watch gameplay only |
| Stage 2 | Understand | Identify behaviors and build episodes |
| Stage 3 | Interact | Press individual keys and observe results |
| Stage 4 | Manipulate | Keyboard + mouse control with continuous observation |
| Stage 5 | Learn | Remember successful and unsuccessful interactions |
| Stage 6 | Act Autonomously | Complete closed-loop experimentation within the environment |

---

# Previous Work

Cassandra originally began as an AI-driven market intelligence platform focused on sentiment analysis, local LLM inference, and equity screening.

Rather than replacing that work, Cassandra now treats it as one application of the broader framework.

Future repositories may include:

- Market Intelligence
- Sports Analytics
- Browser Automation
- Desktop Automation
- Robotics
- QA and Behavioral Testing

All built on the same underlying architecture.

---

# Relationship to OasisAI

Cassandra and OasisAI serve different purposes.

**Cassandra** asks research questions.

- How do models behave?
- What improves performance?
- Which architectural changes matter?

**OasisAI** applies those findings to build practical AI assistants and automation systems.

In short:

```text
Experiments
      │
      ▼
 Cassandra
      │
      ▼
Knowledge
      │
      ▼
 OasisAI
```

---

# Roadmap

- Observation Replay
- Attention Engine
- OCR Sensor
- System Metrics
- Memory Framework
- Environment Plugins
- Comparative Benchmarking
- Remote Execution
- Behavioral Metrics
- Model Evaluation Reports

---

# License

Released under the MIT License.

---

<p align="center">
Cassandra is an open-source research framework developed by Stage One Cloud.

Its purpose is not to prove which AI model is "best," but to better understand how AI systems behave under changing conditions.
</p>
