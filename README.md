<p align="center">
  <img src="https://stageonecloudwebmedia.blob.core.windows.net/webdevmedia/cassandra_banner.png" alt="Cassandra Banner" width="100%"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/LLM-Ollama-000000?style=flat-square&logo=ollama&logoColor=white"/>
  <img src="https://img.shields.io/badge/Sentiment-VADER-4CAF50?style=flat-square"/>
  <img src="https://img.shields.io/badge/Data-yfinance-FF6B35?style=flat-square"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square"/>
  <img src="https://img.shields.io/badge/built_by-Stage_One_Cloud-7DD3FC?style=flat-square"/>
</p>

---

## What is Cassandra?

Cassandra is a modular, AI-driven market intelligence pipeline that collects news, scores sentiment, screens equities, and generates structured investment narratives — using fully local LLM inference with no cloud API dependency.

In Greek mythology, Cassandra was cursed to see the future clearly and never be believed. This pipeline sees market signals. What you do with them is your problem.

Built as a real research tool — not a demo. Every design decision came from running it against live data and documenting what worked, what failed, and why.

---

## Key Capabilities

**News Collection & Sentiment Scoring**
Aggregates RSS feeds across six topic-specific channels — legalization, rescheduling, banking reform, ETFs, multi-state operators, and biomedical. Each article is deduplicated, body-extracted where possible, and scored with VADER sentiment analysis before anything touches the LLM.

**LLM-Driven Market Narratives**
Sends pre-scored article data to a local Ollama instance via HTTP API — no subprocess calls, no cloud dependency. Generates structured five-section investment intelligence reports including regulatory landscape, sector outlook, and key risks.

**Survival-Focused Equity Screening**
Traditional screeners filter cannabis stocks on profitability — which eliminates ~80% of the sector. Cassandra scores on what actually matters for early-stage cannabis equities: cash survival, revenue trajectory, liquidity, momentum, and 52-week positioning.

**Persistent Watchlist**
Flagged candidates are written to a persistent CSV watchlist with entry price and date. The screener updates conviction scores on subsequent runs without losing historical entry data.

**Sector-Agnostic Architecture**
The pipeline is pointed at cannabis because of the Schedule III rescheduling catalyst — but the architecture is domain-agnostic. Swap the RSS feeds, ticker universe, and prompt templates to target any sector, asset class, or data domain.

---

## Architecture

```
                    ┌─────────────────────────────┐
                    │          CASSANDRA          │
                    └──────────────┬──────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│    COLLECT       │    │    ANALYZE       │    │    SCREEN        │
│                  │    │                  │    │                  │
│ feed_to_csv_     │    │ ollama_sentiment │    │ stock_growth_    │
│ collector.py     │    │ pipeline.py      │    │ screener.py      │
│                  │    │                  │    │                  │
│ • 6 topic feeds  │    │ • VADER stats    │    │ • yfinance data  │
│ • Deduplication  │    │ • LLM narrative  │    │ • 6-dim scoring  │
│ • Body extract   │    │ • 5-section      │    │ • Conviction     │
│ • VADER/article  │    │   report         │    │   tiers          │
│ • CSV output     │    │ • MD export      │    │ • Watchlist CSV  │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                       │                       │
         ▼                       ▼                       ▼
  data/cannabis_          reports/sentiment_       reports/screener_
  news_results.csv        report_[ts].md           report_[ts].md
                                                   data/watchlist.csv
         │                       │                        │
         └───────────────────────┴────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │    LOCAL OLLAMA LLM    │
                    │   (no cloud API calls) │
                    │   http://[host]:11434  │
                    └────────────────────────┘
```

Cassandra runs a three-stage pipeline. The **collector** pulls and scores news. The **sentiment pipeline** sends pre-analyzed data to a local Ollama instance for narrative generation. The **screener** pulls live equity data, scores candidates on survival metrics, and maintains a persistent watchlist — all without a single cloud API call for core operations.

---

## Tech Stack

| Layer | Technology | Role |
|---|---|---|
| News Collection | feedparser + BeautifulSoup | RSS aggregation and body extraction |
| Sentiment Scoring | VADER | Per-article sentiment before LLM |
| LLM Inference | Ollama (HTTP API) | Local narrative generation |
| Equity Data | yfinance | Fundamentals and price history |
| Data Layer | pandas + CSV | Pipeline state and watchlist persistence |
| Runtime | Python 3.10+ | Core pipeline language |

---

## Scoring Model

| Dimension | Weight | Rationale |
|---|---|---|
| Price tier | 20pts | Sweet spot $0.10–$10 for high-potential names |
| Liquidity | 15pts | Avg daily volume — can you actually trade it? |
| Cash survival | 25pts | Cash-to-debt ratio — who lives long enough to win? |
| Revenue trajectory | 20pts | Growth rate, even if not yet profitable |
| Price momentum | 10pts | 1-month price change |
| 52w positioning | 10pts | Distance from high — room to run vs broken chart |

**Conviction tiers**: HIGH (65+) · MEDIUM (45–64) · LOW (40–44) · SKIP (<40)

---

## Project Status

| Feature | Status |
|---|---|
| RSS collection across 6 topic channels | ✅ Complete |
| VADER per-article sentiment scoring | ✅ Complete |
| Ollama HTTP API integration | ✅ Complete |
| Survival-focused equity screener | ✅ Complete |
| Persistent watchlist with entry prices | ✅ Complete |
| Timestamped markdown report export | ✅ Complete |
| Social media data layer (Reddit/X) | 📋 Planned |
| Exit signal generation | 📋 Planned |
| Google News URL body resolver | 📋 Planned |
| Domain-agnostic config system | 📋 Planned |
| Sports application (MLB Stats API) | 📋 Planned |
| Scheduled runs via cron/Task Scheduler | 📋 Planned |
| OasisAI Discord alert integration | 📋 Planned |

---

## Honest Disclaimer

Cassandra is a research and portfolio tool — not a trading system.

The v1 of this project flagged IGC Pharma during the cannabis Schedule III rescheduling catalyst in 2024. A $20 test position was opened at $0.42. Current price: ~$0.30.

The entry signal was real. The exit signal didn't exist yet. That's why v2 exists.

*This is not financial advice. Past pipeline output does not guarantee future returns.*

---

## Quick Start

```bash
# Clone
git clone https://github.com/parzival419/cassandra.git
cd cassandra

# Install dependencies
pip install -r requirements.txt

# Step 1 — Collect and score news
python feed_to_csv_collector.py

# Step 2 — Generate sentiment narrative
OLLAMA_HOST=http://localhost:11434 python ollama_sentiment_pipeline.py

# Step 3 — Screen equities and update watchlist
OLLAMA_HOST=http://localhost:11434 python stock_growth_screener.py
```

**Running Ollama on a separate machine:**
```bash
# On the inference machine — bind to all interfaces
OLLAMA_HOST=0.0.0.0 ollama serve

# Point Cassandra at it
OLLAMA_HOST=http://192.168.1.x:11434 python ollama_sentiment_pipeline.py
```

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server address |
| `OLLAMA_MODEL` | `qwen2.5:7b` | Model for analysis |
| `MAX_PRICE` | `15.0` | Max stock price for screening |
| `MAX_AGE_DAYS` | `60` | News lookback window |
| `WATCHLIST_MIN_SCORE` | `40` | Minimum score for watchlist entry |

---

## Built By

**[Stage One Cloud](https://stageonecloud.com)** — Cloud solutions, managed IT services, and AI integration for businesses that want real infrastructure expertise without the enterprise overhead.

---

## Related Projects

- [OasisAI](https://github.com/parzival419/oasisAi) — Self-hosted Discord AI assistant with local LLM inference, persistent memory, and remote infrastructure management

---

<p align="center">
  <sub>Cassandra is an open-source project by Stage One Cloud. MIT licensed — use it, fork it, point it at something other than cannabis stocks. Just don't blame Cassandra when it's right and you don't listen.</sub>
</p>
