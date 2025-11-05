# marketintel-lab

**Modular AI-driven pipeline for market intelligence, sentiment analysis, and trading signal generation.**

`marketintel-lab` is a proof-of-concept project that demonstrates how structured financial data, unstructured news, sentiment scoring, and machine learning can be combined into a lightweight, extensible research tool for financial markets.

This project showcases an end-to-end workflow for collecting news, screening equities, training predictive models, and generating narrative reports using LLMs.

---

## Features

- **News Collection & Sentiment Analysis**
  - RSS feed aggregation for sector- or topic-specific headlines
  - Sentiment scoring using VADER and optional LLM-based summaries
  - Topic filtering, date filtering, and CSV export

- **Fundamental Equity Screening**
  - Pulls stock data from Yahoo Finance via `yfinance`
  - Filters based on valuation, growth, and profitability metrics
  - Designed for low-price, high-potential stock discovery

- **Predictive Modeling**
  - Implements walk-forward validation using:
    - LSTM neural networks (PyTorch)
    - Logistic regression baselines (scikit-learn)
  - Feature set includes technicals, macro signals, and sentiment data
  - Tracks Sharpe, CAGR, MDD, win rate, and trade duration per fold

- **LLM-Based Analysis & Reporting**
  - Integrates with `ollama` for offline local language model summaries
  - Generates structured market narratives and investment outlooks

