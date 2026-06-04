<p align="center">
  <img src="docs/assets/oasisai-banner.png" alt="OasisAI Banner" width="100%"/>
</p>

<h1 align="center">OasisAI</h1>
<p align="center">
  <strong>A self-hosted AI assistant built for real infrastructure management</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Discord-5865F2?style=flat-square&logo=discord&logoColor=white"/>
  <img src="https://img.shields.io/badge/runtime-Hermes_Agent-FF6B35?style=flat-square"/>
  <img src="https://img.shields.io/badge/models-Ollama-000000?style=flat-square&logo=ollama&logoColor=white"/>
  <img src="https://img.shields.io/badge/automation-n8n-EA4B71?style=flat-square&logo=n8n&logoColor=white"/>
  <img src="https://img.shields.io/badge/network-Tailscale-000000?style=flat-square&logo=tailscale&logoColor=white"/>
  <img src="https://img.shields.io/badge/built_by-Stage_One_Cloud-7DD3FC?style=flat-square"/>
</p>

---

## What is OasisAI?

OasisAI is a fully self-hosted AI assistant that lives in Discord and manages real infrastructure. It combines local LLM inference, persistent memory, remote terminal access, and workflow automation — all running on a private home lab with zero cloud API dependency for core operations.

This isn't a chatbot wrapper. It's a working operations tool built to monitor, manage, and maintain servers and workstations across a network.

<p align="center">
  <img src="docs/assets/discord-demo.png" alt="OasisAI Discord Demo" width="600"/>
</p>

---

## Key Capabilities

**Conversational AI with Persistent Memory**
OasisAI remembers context across sessions — user details, machine configurations, project history, and preferences. Every conversation builds on the last.

**Infrastructure Awareness**
The assistant knows the network topology, server specs, running services, and machine roles. Ask it about your environment and it answers from lived context, not a web search.

**Remote Machine Management**
Execute terminal commands on network machines directly from Discord. Check disk space, restart services, pull logs, monitor health — all through natural conversation.

**Automated Monitoring & Alerting**
Scheduled health checks across the network with Discord-based alerting. Proactive notifications before problems become outages.

**Workflow Automation**
Integration with n8n for complex multi-step automations — system status dashboards, scheduled maintenance tasks, and external service integrations.

**Secure Remote Access**
Tailscale mesh VPN integration enables management from anywhere. Portable router support for on-site client deployments.

---

## Architecture

```
                         ┌──────────────┐
                         │   Discord    │
                         │   Server     │
                         └──────┬───────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
              @OasisAI [chat]         ![command]
                    │                       │
                    ▼                       ▼
            ┌──────────────┐       ┌──────────────┐
            │   Hermes     │       │     n8n      │
            │   Agent      │       │  Automation  │
            │              │       │   Engine     │
            │  ┌────────┐  │       └──────┬───────┘
            │  │ Memory  │  │              │
            │  │ Engine  │  │              │
            │  └────────┘  │              │
            └──────┬───────┘              │
                   │                      │
         ┌─────────┴──────────┐           │
         │                    │           │
         ▼                    ▼           ▼
  ┌─────────────┐    ┌──────────────┐  ┌──────────┐
  │   Atlas     │    │   Mercury    │  │ Client   │
  │  (Server)   │    │  (Inference) │  │ Networks │
  │             │    │              │  │          │
  │  Ubuntu     │    │  Windows     │  │ Via      │
  │  Hermes     │    │  Ollama      │  │ Tailscale│
  │  n8n        │    │  Local LLMs  │  │          │
  │  Tailscale  │    │  Tailscale   │  │          │
  └─────────────┘    └──────────────┘  └──────────┘
```

OasisAI runs on a two-machine architecture. The **server node** handles the agent runtime, memory persistence, automation engine, and Discord gateway. The **inference node** runs Ollama with local LLM models, keeping all AI processing on the private network. A Tailscale mesh VPN extends management reach to remote client networks.

---

## Tech Stack

| Layer | Technology | Role |
|---|---|---|
| AI Runtime | Hermes Agent | Agent framework with memory, tool use, and gateway |
| LLM Inference | Ollama | Local model serving (OpenAI-compatible API) |
| Chat Interface | Discord | Primary user interface with threading |
| Automation | n8n | Workflow automation and external integrations |
| Networking | Tailscale | Mesh VPN for secure remote access |
| Server OS | Ubuntu 26.04 | Production server platform |
| Memory | Markdown-based | Persistent, human-readable, version-controllable |

---

## Project Status

| Feature | Status |
|---|---|
| Discord integration with threading | ✅ Complete |
| Persistent memory across sessions | ✅ Complete |
| Custom persona (SOUL.md) | ✅ Complete |
| Tailscale mesh VPN | ✅ Complete |
| Remote terminal execution | 🔧 In Progress |
| n8n command workflows | 🔧 In Progress |
| Automated health monitoring | 📋 Planned |
| Multi-client network management | 📋 Planned |
| ElevenLabs voice integration | 📋 Planned |
| Slash commands | 📋 Planned |

---

## Screenshots

<p align="center">
  <img src="docs/assets/memory-recall.png" alt="Memory Recall" width="45%"/>
  &nbsp;&nbsp;
  <img src="docs/assets/discord-thread.png" alt="Discord Threading" width="45%"/>
</p>

<p align="center">
  <em>Left: OasisAI recalling infrastructure details from persistent memory. Right: Automatic thread creation for organized conversations.</em>
</p>

---

## Why Self-Hosted?

- **Data sovereignty** — All conversations, memory, and infrastructure data stay on your network
- **No recurring API costs** for core operations — inference runs on hardware you own
- **Full customization** — persona, memory, tools, and workflows are all configurable
- **Network-aware** — the assistant understands your actual infrastructure, not generic cloud resources
- **Portable** — the entire stack can be replicated for client deployments

---

## Built By

**[Stage One Cloud](https://stageonecloud.com)** — Cloud solutions, managed IT services, and AI integration for businesses that want real infrastructure expertise without the enterprise overhead.

---

<p align="center">
  <sub>OasisAI is a proprietary project by Stage One Cloud. This repository serves as a project overview and portfolio piece. Implementation details, configurations, and deployment guides are not included.</sub>
</p>
