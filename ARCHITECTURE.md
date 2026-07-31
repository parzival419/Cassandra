\# Cassandra Architecture



> This document describes the architectural principles behind Cassandra.

>

> While the codebase will evolve, the design philosophy documented here should

> remain stable unless an intentional architectural decision is made.



\---



\# Vision



Cassandra is an environment-agnostic AI behavioral research framework.



Its purpose is to observe, evaluate, and understand how AI systems behave

under changing environments and constraints.



Cassandra is not tied to a single model, application, or domain.



Instead, it provides a reusable framework for building experiments and

applications that require structured observation and reasoning.



\---



\# Design Principles



\## Domain Driven Design



Cassandra is modeled around real-world concepts rather than implementation details.



Examples include:



\- Observation

\- Environment

\- Sensor

\- Experiment

\- Planner

\- Memory

\- Evaluation



These concepts are represented as first-class objects within the framework.



\---



\## Single Responsibility Principle



Every object should have one clearly defined responsibility.



Examples:



ObservationEngine



Responsible for coordinating sensors and producing an Observation.



WindowSensor



Responsible only for gathering window information.



Observation



Represents the result of a completed observation.



\---



\## Composition Over Inheritance



Whenever practical, Cassandra favors composition over deep inheritance.



Objects should be assembled from smaller components with well-defined

responsibilities.



Example:



Observation



contains



\- EnvironmentInfo

\- VisualData

\- Metadata

\- State



rather than inheriting behavior from multiple parent classes.



\---



\## Explicit Interfaces



Core framework components communicate through explicit contracts.



The goal is to allow components to be replaced or extended without changing

the rest of the framework.



Future examples include:



\- Sensor

\- Environment

\- Planner



\---



\## Environment Agnostic



Cassandra should never assume a specific environment.



Examples of environments include:



\- Games

\- Desktop applications

\- Browsers

\- Simulations

\- APIs

\- Future research environments



The framework should interact with all environments through common abstractions.



\---



\# Repository Layout



Cassandra/



README.md

User documentation.



ARCHITECTURE.md

Framework architecture and design philosophy.



cassandra/

Core framework implementation.



experiments/

Research environments used to evaluate AI behavior.



modules/

Real-world applications built on Cassandra.



docs/

Additional documentation.



\---



\# Architectural Decisions



\## ADR-001



Title



Observation is a first-class domain object.



Status



Accepted



Reason



An observation represents a complete snapshot of an environment.



It is the common language shared by sensors, planners, memory,

evaluation, and future modules.



Observations are represented as structured objects rather than dictionaries.



Date



2026-07-30



\---



\## ADR-002



Title



ObservationEngine orchestrates sensors.



Status



Accepted



Reason



Sensors should remain independent.



The ObservationEngine is responsible for coordinating sensor execution and

assembling the resulting Observation.



Date



Pending



\---



\# Long-Term Goals



The Cassandra Core framework should remain independent from any individual

experiment or application.



Experiments exist to answer research questions.



Modules exist to solve real-world problems.



Both are built upon the same core framework.



\---



\# Guiding Question



Whenever a new feature is proposed, ask:



"Does this belong in Cassandra Core, an Experiment, or a Module?"



If the answer is unclear, the design should be reconsidered before implementation.

