"""
stock_growth_screener.py
------------------------
Screens a cannabis stock universe using survival-focused metrics
appropriate for the sector (not traditional profitability filters).
Scores each candidate on multiple dimensions, generates a conviction
ranking, and maintains a persistent watchlist with entry prices.

Run after feed_to_csv_collector.py so sentiment context is available.
"""

import json
import os
import sys
from datetime import datetime, date

import numpy as np
import pandas as pd
import requests
import yfinance as yf

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_DIR       = os.path.join(os.path.dirname(__file__), "data")
WATCHLIST_FILE = os.path.join(DATA_DIR, "watchlist.csv")
REPORT_DIR     = os.path.join(os.path.dirname(__file__), "reports")
SENTIMENT_CSV  = os.path.join(DATA_DIR, "cannabis_news_results.csv")

OLLAMA_HOST    = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL   = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")

# Max price filter — we're looking for cheap, high-potential names
MAX_PRICE      = 15.0

# Minimum score (0–100) to be added to watchlist
WATCHLIST_MIN_SCORE = 40

# ---------------------------------------------------------------------------
# Cannabis Universe
# ---------------------------------------------------------------------------
# Honest note: this is a curated starting list, not exhaustive.
# OTC tickers (CURLF, TCNNF etc.) are US-listed but trade OTC because
# cannabis is still federally illegal for major exchange listing.
# Schedule III rescheduling may change this — worth monitoring.

CANNABIS_UNIVERSE = [
    # Multi-State Operators (MSOs) — retail/dispensary focus
    "CURLF",   # Curaleaf
    "TCNNF",   # Trulieve
    "GTBIF",   # Green Thumb Industries
    "CRLBF",   # Cresco Labs
    "VRNOF",   # Verano Holdings
    "AYRWF",   # Ayr Wellness
    "JUSHF",   # Jushi Holdings
    "HRVSF",   # Harvest Health

    # Biomedical / Pharmaceutical
    "IGC",     # IGC Pharma (NYSE listed)
    "GWPH",    # GW Pharmaceuticals (acquired by Jazz, may be delisted)
    "CBST",    # Cannabist Health (formerly Columbia Care)
    "MJNA",    # Medical Marijuana Inc

    # ETFs — useful as sector sentiment benchmarks, not individual picks
    "MSOS",    # AdvisorShares Pure US Cannabis ETF
    "YOLO",    # AdvisorShares Pure Cannabis ETF
    "MJ",      # ETFMG Alternative Harvest ETF
]

# ---------------------------------------------------------------------------
# Data Fetching
# ---------------------------------------------------------------------------

def fetch_ticker_data(symbol: str) -> dict:
    """
    Fetch fundamentals and recent price history for a single ticker.
    Returns a flat dict of the fields we care about.
    """
    result = {
        "symbol"         : symbol,
        "current_price"  : None,
        "market_cap"     : None,
        "total_revenue"  : None,
        "revenue_growth" : None,
        "total_cash"     : None,
        "total_debt"     : None,
        "current_ratio"  : None,
        "profit_margin"  : None,
        "52w_high"       : None,
        "52w_low"        : None,
        "avg_volume"     : None,
        "price_1m_chg"   : None,
        "price_3m_chg"   : None,
        "fetch_error"    : None,
    }

    try:
        ticker = yf.Ticker(symbol)
        info   = ticker.info or {}

        # Price — try multiple fields yfinance uses inconsistently
        price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or info.get("navPrice")
        )
        if not price:
            hist = ticker.history(period="5d")
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])

        result["current_price"]  = price
        result["market_cap"]     = info.get("marketCap")
        result["total_revenue"]  = info.get("totalRevenue")
        result["revenue_growth"] = info.get("revenueGrowth")   # decimal e.g. 0.12
        result["total_cash"]     = info.get("totalCash")
        result["total_debt"]     = info.get("totalDebt")
        result["current_ratio"]  = info.get("currentRatio")
        result["profit_margin"]  = info.get("profitMargins")   # decimal
        result["52w_high"]       = info.get("fiftyTwoWeekHigh")
        result["52w_low"]        = info.get("fiftyTwoWeekLow")
        result["avg_volume"]     = info.get("averageVolume")

        # Short-term price momentum
        hist_3m = ticker.history(period="3mo")
        if len(hist_3m) >= 2:
            start_price = float(hist_3m["Close"].iloc[0])
            end_price   = float(hist_3m["Close"].iloc[-1])
            result["price_3m_chg"] = (end_price - start_price) / start_price if start_price else None

            # 1-month from the last 30 trading days
            if len(hist_3m) >= 21:
                start_1m = float(hist_3m["Close"].iloc[-21])
                result["price_1m_chg"] = (end_price - start_1m) / start_1m if start_1m else None

    except Exception as e:
        result["fetch_error"] = str(e)

    return result


def fetch_universe(symbols: list) -> pd.DataFrame:
    """Fetch data for all symbols, return as DataFrame."""
    print(f"\n📊 Fetching data for {len(symbols)} tickers...")
    rows = []
    for sym in symbols:
        print(f"  → {sym}", end="  ")
        data = fetch_ticker_data(sym)
        if data["fetch_error"]:
            print(f"⚠️  {data['fetch_error'][:60]}")
        elif data["current_price"]:
            print(f"${data['current_price']:.2f}")
        else:
            print("no price")
        rows.append(data)

    df = pd.DataFrame(rows)
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(os.path.join(DATA_DIR, "raw_universe.csv"), index=False)
    return df


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
# Realistic scoring for cannabis sector:
# We are NOT filtering on profitability — almost none of these are profitable.
# We ARE scoring on:
#   1. Price positioning   — cheap, but not penny-stock noise
#   2. Liquidity           — enough volume to actually trade
#   3. Cash survival       — cash vs debt ratio (who lives long enough to win)
#   4. Revenue trajectory  — are they growing even if not profitable?
#   5. Price momentum      — is the market starting to notice?
#   6. 52w positioning     — how far off the high (room to run vs dead cat)

def _safe(val, default=0.0):
    """Return val if it's a valid number, else default."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return default
    return float(val)


def score_ticker(row: pd.Series) -> dict:
    """
    Score a single ticker 0-100 across 6 dimensions.
    Returns a dict of dimension scores and a composite.
    """
    scores = {}

    # 1. Price (0-20): sweet spot $0.10–$10, penalize sub-penny noise
    price = _safe(row.get("current_price"))
    if 0.10 <= price <= 2.0:
        scores["price"] = 20
    elif 2.0 < price <= 5.0:
        scores["price"] = 15
    elif 5.0 < price <= MAX_PRICE:
        scores["price"] = 10
    elif price > MAX_PRICE:
        scores["price"] = 0   # above our range
    else:
        scores["price"] = 0   # sub-penny / no data

    # 2. Liquidity (0-15): avg daily volume
    vol = _safe(row.get("avg_volume"))
    if vol >= 1_000_000:
        scores["liquidity"] = 15
    elif vol >= 500_000:
        scores["liquidity"] = 10
    elif vol >= 100_000:
        scores["liquidity"] = 5
    else:
        scores["liquidity"] = 0

    # 3. Cash survival (0-25): cash-to-debt ratio
    cash = _safe(row.get("total_cash"))
    debt = _safe(row.get("total_debt"), default=1.0)
    ratio = cash / debt if debt > 0 else 0
    if ratio >= 1.0:
        scores["cash_survival"] = 25   # more cash than debt — strong
    elif ratio >= 0.5:
        scores["cash_survival"] = 15
    elif ratio >= 0.25:
        scores["cash_survival"] = 8
    else:
        scores["cash_survival"] = 0    # heavily indebted, survival risk

    # 4. Revenue trajectory (0-20): growth rate (can be negative)
    rev_growth = _safe(row.get("revenue_growth"))
    if rev_growth >= 0.15:
        scores["revenue"] = 20
    elif rev_growth >= 0.05:
        scores["revenue"] = 14
    elif rev_growth >= 0.0:
        scores["revenue"] = 8
    elif rev_growth >= -0.10:
        scores["revenue"] = 3    # declining but not collapsing
    else:
        scores["revenue"] = 0    # significant revenue decline

    # 5. Price momentum (0-10): 1-month change
    mom_1m = _safe(row.get("price_1m_chg"))
    if mom_1m >= 0.10:
        scores["momentum"] = 10
    elif mom_1m >= 0.03:
        scores["momentum"] = 7
    elif mom_1m >= -0.05:
        scores["momentum"] = 4
    else:
        scores["momentum"] = 0

    # 6. 52-week positioning (0-10): distance below 52w high
    high_52w = _safe(row.get("52w_high"))
    low_52w  = _safe(row.get("52w_low"))
    price_now = price
    if high_52w > 0 and price_now > 0:
        pct_from_high = (high_52w - price_now) / high_52w
        if 0.30 <= pct_from_high <= 0.65:
            scores["positioning"] = 10   # meaningful pullback, not broken
        elif pct_from_high < 0.30:
            scores["positioning"] = 6    # near highs — less upside
        elif pct_from_high <= 0.80:
            scores["positioning"] = 3    # deep discount — may be broken
        else:
            scores["positioning"] = 0    # near all-time low
    else:
        scores["positioning"] = 0

    composite = sum(scores.values())
    scores["composite"] = composite

    # Human-readable conviction tier
    if composite >= 65:
        scores["conviction"] = "HIGH"
    elif composite >= 45:
        scores["conviction"] = "MEDIUM"
    elif composite >= WATCHLIST_MIN_SCORE:
        scores["conviction"] = "LOW"
    else:
        scores["conviction"] = "SKIP"

    return scores


def apply_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Score all tickers and merge scores back into dataframe."""
    score_rows = []
    for _, row in df.iterrows():
        s = score_ticker(row)
        score_rows.append(s)

    scores_df = pd.DataFrame(score_rows)
    result = pd.concat([df.reset_index(drop=True), scores_df], axis=1)
    result = result.sort_values("composite", ascending=False)
    return result


# ---------------------------------------------------------------------------
# Sentiment overlay
# ---------------------------------------------------------------------------

def get_sector_sentiment(csv_path: str) -> dict:
    """Pull aggregate sentiment from the news collector output."""
    if not os.path.exists(csv_path):
        return {}
    try:
        df = pd.read_csv(csv_path)
        avg = df["sentiment_compound"].mean() if "sentiment_compound" in df.columns else 0
        label = "positive" if avg >= 0.05 else ("negative" if avg <= -0.05 else "neutral")
        return {
            "avg_compound"  : round(avg, 4),
            "overall_label" : label,
            "article_count" : len(df),
        }
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Watchlist management
# ---------------------------------------------------------------------------

def load_watchlist() -> pd.DataFrame:
    if os.path.exists(WATCHLIST_FILE):
        return pd.read_csv(WATCHLIST_FILE)
    return pd.DataFrame(columns=[
        "symbol", "added_date", "entry_price", "conviction",
        "composite_score", "notes"
    ])


def update_watchlist(screened_df: pd.DataFrame, current_df: pd.DataFrame):
    """
    Add new HIGH/MEDIUM conviction names to watchlist.
    Update price and score for existing entries.
    Does not remove entries — use notes field to manually mark exits.
    """
    watchlist = load_watchlist()
    existing  = set(watchlist["symbol"].tolist()) if not watchlist.empty else set()
    new_rows  = []

    for _, row in screened_df.iterrows():
        sym = row["symbol"]
        if row["conviction"] in ("HIGH", "MEDIUM") and sym not in existing:
            new_rows.append({
                "symbol"         : sym,
                "added_date"     : date.today().isoformat(),
                "entry_price"    : row.get("current_price"),
                "conviction"     : row["conviction"],
                "composite_score": row["composite"],
                "notes"          : "",
            })
            print(f"  ➕ Added to watchlist: {sym} ({row['conviction']} | score {row['composite']})")

        elif sym in existing:
            # Update score for existing positions
            idx = watchlist[watchlist["symbol"] == sym].index
            if not idx.empty:
                watchlist.loc[idx[0], "composite_score"] = row["composite"]
                watchlist.loc[idx[0], "conviction"]      = row["conviction"]

    if new_rows:
        watchlist = pd.concat([watchlist, pd.DataFrame(new_rows)], ignore_index=True)

    os.makedirs(DATA_DIR, exist_ok=True)
    watchlist.to_csv(WATCHLIST_FILE, index=False)
    print(f"  💾 Watchlist saved → {WATCHLIST_FILE} ({len(watchlist)} entries)")
    return watchlist


# ---------------------------------------------------------------------------
# Ollama analysis
# ---------------------------------------------------------------------------

def build_screener_prompt(scored_df: pd.DataFrame, sentiment: dict) -> str:
    # Only send watchlist-worthy candidates to the LLM
    candidates = scored_df[scored_df["conviction"] != "SKIP"].head(10)

    if candidates.empty:
        return ""

    sector_ctx = ""
    if sentiment:
        sector_ctx = (
            f"Current sector sentiment: {sentiment.get('overall_label', 'unknown')} "
            f"(VADER avg compound: {sentiment.get('avg_compound', 0):+.4f}, "
            f"based on {sentiment.get('article_count', 0)} recent articles)\n\n"
        )

    stocks_block = ""
    for _, row in candidates.iterrows():
        stocks_block += (
            f"---\n"
            f"Ticker         : {row['symbol']}\n"
            f"Price          : ${_safe(row.get('current_price')):.2f}\n"
            f"Market Cap     : ${_safe(row.get('market_cap')):,.0f}\n"
            f"Revenue Growth : {_safe(row.get('revenue_growth')) * 100:.1f}%\n"
            f"Cash/Debt Ratio: {(_safe(row.get('total_cash')) / max(_safe(row.get('total_debt'), 1), 1)):.2f}\n"
            f"1M Price Chg   : {_safe(row.get('price_1m_chg')) * 100:.1f}%\n"
            f"Conviction     : {row.get('conviction', 'N/A')} (score {row.get('composite', 0)}/100)\n"
        )

    prompt = f"""You are a cannabis sector equity analyst. The following stocks passed a quantitative screening process designed for the cannabis industry, which accounts for the fact that most cannabis companies are not yet profitable.

{sector_ctx}Screening criteria used:
- Price under ${MAX_PRICE} (targeting high-potential small caps)
- Scored on: liquidity, cash-to-debt survival ratio, revenue trajectory, price momentum, and 52-week positioning
- NOT filtered on profitability (unrealistic for this sector)

Screened candidates:
{stocks_block}

For each candidate provide:
1. A 2-3 sentence assessment of its risk/reward profile given the current regulatory environment (Schedule III rescheduling, SAFER Banking Act status)
2. One specific risk that could invalidate the thesis for this name
3. A verdict: WATCH, AVOID, or RESEARCH MORE

End with a brief paragraph on whether current sector conditions favor entry or patience.

Be direct and realistic. Do not recommend actual buy amounts or act as a financial advisor.
"""
    return prompt.strip()


def call_ollama(prompt: str) -> str:
    url     = f"{OLLAMA_HOST}/api/generate"
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    print(f"\n🧠 Sending screened candidates to Ollama ({OLLAMA_MODEL})...")
    try:
        r = requests.post(url, json=payload, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to Ollama at {OLLAMA_HOST}")
        print("   Make sure Ollama is running: `ollama serve`")
        return ""
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return ""


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def save_report(scored_df: pd.DataFrame, llm_text: str, sentiment: dict):
    os.makedirs(REPORT_DIR, exist_ok=True)
    ts          = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORT_DIR, f"screener_report_{ts}.md")

    candidates  = scored_df[scored_df["conviction"] != "SKIP"]
    skipped     = scored_df[scored_df["conviction"] == "SKIP"]

    rows_md = ""
    for _, r in scored_df.iterrows():
        rows_md += (
            f"| {r['symbol']:8s} | ${_safe(r.get('current_price')):6.2f} "
            f"| {r.get('conviction', ''):7s} | {r.get('composite', 0):3.0f}/100 "
            f"| {_safe(r.get('revenue_growth'))*100:+.1f}% "
            f"| {_safe(r.get('price_1m_chg'))*100:+.1f}% |\n"
        )

    report = f"""# 🌿 Cannabis Stock Screener Report
**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Universe**: {len(scored_df)} tickers screened
**Model**: {OLLAMA_MODEL}

## Sector Sentiment Context
| Metric | Value |
|--------|-------|
| Overall label | {sentiment.get('overall_label', 'N/A')} |
| VADER avg compound | {sentiment.get('avg_compound', 0):+.4f} |
| Articles analyzed | {sentiment.get('article_count', 'N/A')} |

## Screening Results
| Ticker | Price | Conviction | Score | Rev Growth | 1M Chg |
|--------|-------|-----------|-------|-----------|--------|
{rows_md}

**Watchlist candidates**: {len(candidates)} | **Skipped**: {len(skipped)}

---

## LLM Analysis

{llm_text if llm_text else "_Ollama not available — run with Ollama serving on localhost:11434_"}
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    return report_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("🌿 Cannabis Stock Screener v2")
    print(f"   Universe  : {len(CANNABIS_UNIVERSE)} tickers")
    print(f"   Max price : ${MAX_PRICE}")
    print(f"   Min score : {WATCHLIST_MIN_SCORE}/100 for watchlist")

    # 1. Fetch
    raw_df = fetch_universe(CANNABIS_UNIVERSE)

    # 2. Filter out tickers with no price data
    valid_df = raw_df[raw_df["current_price"].notna() & (raw_df["current_price"] > 0)].copy()
    print(f"\n✅ {len(valid_df)}/{len(raw_df)} tickers returned price data")

    if valid_df.empty:
        print("❌ No valid data. Check network access to Yahoo Finance.")
        sys.exit(1)

    # 3. Score
    scored_df = apply_scores(valid_df)

    # 4. Print summary table
    print("\n📋 Scoring Results:")
    print(f"{'Ticker':8s} {'Price':>7s} {'Score':>6s} {'Conviction':10s} {'RevGrowth':>10s} {'1M Chg':>8s}")
    print("-" * 58)
    for _, row in scored_df.iterrows():
        print(
            f"{row['symbol']:8s} "
            f"${_safe(row.get('current_price')):6.2f} "
            f"{row.get('composite', 0):>6.0f} "
            f"{row.get('conviction', ''):10s} "
            f"{_safe(row.get('revenue_growth'))*100:>+9.1f}% "
            f"{_safe(row.get('price_1m_chg'))*100:>+7.1f}%"
        )

    # 5. Watchlist
    print("\n📌 Updating watchlist...")
    watchlist = update_watchlist(scored_df, raw_df)

    # 6. Sentiment overlay
    sentiment = get_sector_sentiment(SENTIMENT_CSV)
    if sentiment:
        print(f"\n📰 Sector sentiment: {sentiment['overall_label']} ({sentiment['avg_compound']:+.4f})")

    # 7. LLM analysis
    prompt   = build_screener_prompt(scored_df, sentiment)
    llm_text = call_ollama(prompt) if prompt else ""

    if llm_text:
        print("\n📈 LLM Analysis:\n")
        print(llm_text)

    # 8. Save report
    report_path = save_report(scored_df, llm_text, sentiment)
    print(f"\n📄 Report saved → {report_path}")


if __name__ == "__main__":
    main()
