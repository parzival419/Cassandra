"""
ollama_sentiment_pipeline.py
-----------------------------
Reads the collected news CSV, computes aggregate VADER sentiment statistics,
then sends a structured prompt to a local Ollama instance via HTTP API
for deeper LLM-based narrative analysis. Saves a markdown report.
"""

import json
import os
import sys
from datetime import datetime

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_DIR    = os.path.join(os.path.dirname(__file__), "data")
INPUT_CSV   = os.path.join(DATA_DIR, "cannabis_news_results.csv")
REPORT_DIR  = os.path.join(os.path.dirname(__file__), "reports")

OLLAMA_HOST  = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")  # override via env var

MAX_ARTICLES_FOR_LLM = 40   # keep prompt size reasonable
MAX_BODY_CHARS       = 600  # truncate long bodies before sending to LLM

# ---------------------------------------------------------------------------
# Data loading & VADER aggregation
# ---------------------------------------------------------------------------

def load_data(path: str, max_age_days: int = 60) -> pd.DataFrame:
    if not os.path.exists(path):
        print(f"❌ Input file not found: {path}")
        print("   Run feed_to_csv_collector.py first.")
        sys.exit(1)

    df = pd.read_csv(path)
    print(f"✅ Loaded {len(df)} articles from {path}")

    df["published"] = pd.to_datetime(df["published"], errors="coerce", utc=True)
    df = df.dropna(subset=["published"])

    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=max_age_days)
    df = df[df["published"] >= cutoff]
    print(f"🕒 {len(df)} articles within the last {max_age_days} days")
    return df


def compute_vader_summary(df: pd.DataFrame) -> dict:
    """Aggregate VADER scores already computed by the collector."""
    if "sentiment_compound" not in df.columns:
        return {}

    label_counts = df["sentiment_label"].value_counts().to_dict() if "sentiment_label" in df.columns else {}
    avg_compound  = df["sentiment_compound"].mean()
    topic_sentiment = (
        df.groupby("topic")["sentiment_compound"]
        .mean()
        .round(4)
        .to_dict()
    )

    return {
        "total_articles"  : len(df),
        "label_counts"    : label_counts,
        "avg_compound"    : round(avg_compound, 4),
        "overall_label"   : "positive" if avg_compound >= 0.05 else ("negative" if avg_compound <= -0.05 else "neutral"),
        "topic_sentiment" : topic_sentiment,
    }


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def build_prompt(df: pd.DataFrame, vader_summary: dict) -> str:
    subset = df.head(MAX_ARTICLES_FOR_LLM)

    articles_block = ""
    for _, row in subset.iterrows():
        title  = str(row.get("title", "")).strip()
        body   = str(row.get("body", "")).strip()
        source = str(row.get("source", "")).strip()
        label  = str(row.get("sentiment_label", "")).strip()
        score  = row.get("sentiment_compound", 0)
        topic  = str(row.get("topic", "")).strip()

        short_body = (body[:MAX_BODY_CHARS] + "...") if len(body) > MAX_BODY_CHARS else body

        articles_block += (
            f"---\n"
            f"Topic     : {topic}\n"
            f"Title     : {title}\n"
            f"Source    : {source}\n"
            f"Sentiment : {label} ({score:+.3f})\n"
        )
        if short_body:
            articles_block += f"Body      : {short_body}\n"

    vader_block = ""
    if vader_summary:
        vader_block = f"""
Pre-computed VADER sentiment statistics:
- Total articles analyzed : {vader_summary.get('total_articles', 'N/A')}
- Overall sentiment       : {vader_summary.get('overall_label', 'N/A')} (avg compound: {vader_summary.get('avg_compound', 0):+.4f})
- Label breakdown         : {vader_summary.get('label_counts', {})}
- Sentiment by topic      :
"""
        for topic, score in vader_summary.get("topic_sentiment", {}).items():
            vader_block += f"    {topic[:50]:50s} {score:+.4f}\n"

    prompt = f"""You are a senior financial and policy analyst specializing in cannabis sector equities.

{vader_block}

Your task is to analyze the following {len(subset)} cannabis-related news articles and produce a structured investment intelligence report.

Your report MUST include these sections:

1. OVERALL SENTIMENT
   Classify the general tone as positive, negative, or mixed. Reference the VADER statistics above and explain whether the LLM reading agrees or diverges.

2. NARRATIVE SUMMARY (400-500 words)
   Describe the dominant themes, tone shifts, and storylines driving cannabis news right now. What is the market narrative?

3. REGULATORY & POLITICAL LANDSCAPE
   Summarize any developments in Schedule III rescheduling, SAFER Banking Act, state-level legalization, or DEA/FDA actions.

4. INVESTMENT OUTLOOK
   Separate your analysis into two categories:
   a) Multi-state operators and retail cannabis (dispensaries, MSOs)
   b) Biomedical and pharmaceutical cannabis (clinical trials, drug development)
   For each: what does recent news imply about near-term risk and opportunity?

5. KEY RISKS TO WATCH
   List 3-5 specific risks that could invalidate a bullish thesis on cannabis equities right now.

6. ARTICLES REVIEWED
   State how many articles were analyzed.

Articles:
{articles_block}
"""
    return prompt.strip()


# ---------------------------------------------------------------------------
# Ollama HTTP API call
# ---------------------------------------------------------------------------

def call_ollama(prompt: str, model: str, host: str) -> str:
    url = f"{host}/api/generate"
    payload = {
        "model"  : model,
        "prompt" : prompt,
        "stream" : False,
    }

    print(f"\n🧠 Sending to Ollama ({model}) at {host}...")
    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()

    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to Ollama at {host}")
        print("   Make sure Ollama is running: `ollama serve`")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("❌ Ollama request timed out (300s). Try a smaller model.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ollama API error: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Report saving
# ---------------------------------------------------------------------------

def save_report(llm_text: str, vader_summary: dict, model: str) -> str:
    os.makedirs(REPORT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORT_DIR, f"sentiment_report_{timestamp}.md")

    label_counts = vader_summary.get("label_counts", {})
    topic_lines  = "\n".join(
        f"| {t[:55]:55s} | {s:+.4f} |"
        for t, s in vader_summary.get("topic_sentiment", {}).items()
    )

    header = f"""# 🌿 Cannabis Market Sentiment Report
**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Model**: {model}
**Articles analyzed**: {vader_summary.get('total_articles', 'N/A')}

## VADER Pre-Analysis
| Metric | Value |
|--------|-------|
| Overall label | {vader_summary.get('overall_label', 'N/A')} |
| Avg compound score | {vader_summary.get('avg_compound', 0):+.4f} |
| Positive articles | {label_counts.get('positive', 0)} |
| Neutral articles  | {label_counts.get('neutral', 0)} |
| Negative articles | {label_counts.get('negative', 0)} |

### Sentiment by Topic
| Topic | Avg Compound |
|-------|-------------|
{topic_lines}

---

## LLM Analysis

{llm_text}
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(header)

    return report_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    df = load_data(INPUT_CSV)

    if df.empty:
        print("❌ No articles to analyze after date filtering.")
        sys.exit(1)

    vader_summary = compute_vader_summary(df)

    print("\n📊 VADER Summary:")
    print(f"   Overall : {vader_summary.get('overall_label')} ({vader_summary.get('avg_compound'):+.4f})")
    for label, count in vader_summary.get("label_counts", {}).items():
        print(f"   {label:10s}: {count}")

    prompt      = build_prompt(df, vader_summary)
    llm_output  = call_ollama(prompt, OLLAMA_MODEL, OLLAMA_HOST)

    print("\n📈 LLM Analysis:\n")
    print(llm_output)

    report_path = save_report(llm_output, vader_summary, OLLAMA_MODEL)
    print(f"\n📄 Report saved → {report_path}")


if __name__ == "__main__":
    main()
