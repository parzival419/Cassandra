# Cassandra

Cassandra is an experimental AI research platform for studying how language models observe, reason, adapt, and act within controlled environments.

The project explores a simple question:

> How much of an AI system's capability comes from the model itself, and how much comes from the architecture surrounding it?

Rather than treating the LLM as the entire system, Cassandra separates observation, evaluation, memory, planning, and action into independent components. This makes it possible to study how different models behave under the same goals, environments, and constraints.

## Current Architecture

Cassandra is being developed around a behavioral loop:

**Observe → Evaluate → Remember → Plan → Act → Observe**

The current framework includes:

- Desktop observation and state normalization
- Behavioral event detection
- Episodic memory and behavioral summaries
- Persistent experiments and missions
- Prioritized objectives and objective lifecycle tracking
- Deterministic objective selection
- Automated testing of behavioral and planning components

## Current Experiment

### Experiment 001: The Farmer Was Replaced

The first controlled environment uses *The Farmer Was Replaced* to study how an LLM approaches iterative programming tasks.

The long-term experiment will allow a model to:

1. Receive a high-level mission and objectives
2. Observe the environment
3. Determine its current objective
4. Generate and execute candidate code
5. Observe the result
6. Evaluate what changed
7. Retain useful behavioral history
8. Adapt future attempts based on previous outcomes

The goal is not to build the best farming bot. The game provides a repeatable environment for studying model behavior, planning, failure, adaptation, and learning.

## Research Areas

- Agentic AI systems
- Local language models
- Behavioral evaluation
- Episodic memory
- Goal-directed planning
- AI observability
- Human-defined constraints and objectives
- Model and system architecture comparison

## Status

Cassandra is currently under active development.

The behavioral observation, evaluation, memory, experiment, and initial objective-planning layers are functional and covered by automated tests. Work is now moving toward plan generation and the first end-to-end interaction with the experimental environment.
