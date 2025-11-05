import pandas as pd
import subprocess
import os
from datetime import datetime, timedelta

# -----------------------------
# Configuration
# -----------------------------
CSV_PATH = r"F:\\Code_output\\cannabis_news_results.csv"
MODEL = "llama2-uncensored"
REPORT_PATH = "sentiment_analysis.md"


def load_news_data(path, max_age_days=180):
    try:
        df = pd.read_csv(path)
        print(f"✅ Loaded {len(df)} total articles from {path}")

        # Ensure 'Published' is a datetime column
        df['Published'] = pd.to_datetime(df['Published'], errors='coerce')

        # Filter out rows with invalid or missing dates
        df = df.dropna(subset=["Published"])

        # Keep only rows within the last 180 days
        cutoff = datetime.now() - timedelta(days=max_age_days)
        recent_df = df[df["Published"] >= cutoff]

        print(f"🕒 Retained {len(recent_df)} articles from the last {max_age_days} days")
        return recent_df

    except Exception as e:
        print(f"❌ Failed to load or filter data: {e}")
        return pd.DataFrame()

def prepare_prompt(news_df, max_articles=50):
    subset = news_df.head(max_articles)
    combined = ""

    for idx, row in subset.iterrows():
        title = row.get("Title", "").strip()
        body = row.get("Body", "").strip()
        link = row.get("Link", "").strip()

        if not body:
            continue  # Skip empty articles

        # Truncate body if it's too long
        short_body = (body[:800] + "...") if len(body) > 800 else body

        combined += (
            f"---\n"
            f"📰 **Title:** {title}\n"
            f"📝 **Summary:** {short_body}\n"
            f"🔗 **Link:** {link}\n"
        )

    prompt = f"""
You are a seasoned policy and financial analyst. Carefully analyze the following cannabis-related news articles.

Your Task:

Provide a comprehensive analysis of the following cannabis-related news articles. Your response should include:

1. **Overall Sentiment** — Classify the general tone of recent cannabis news as **positive**, **negative**, or **mixed**, based on the mood of headlines and reporting.

2. **500-Word Summary** — Deliver a detailed narrative summarizing public and investor sentiment. Highlight major themes, tone shifts, emotional cues, and key headlines influencing market perception.

3. **Regulatory and Political Insights** — Summarize any developments in U.S. federal or state cannabis legislation, DEA scheduling, or banking reform efforts (such as the SAFER Banking Act).

4. **Investment Outlook** — Assess the current investment climate for cannabis-related equities.  
   - Distinguish between **retail-focused** cannabis companies (dispensaries, MSOs, consumer brands) and **biomedical or pharmaceutical** cannabis firms.  
   - Provide a sentiment-driven perspective on whether it is advisable to invest in each category based on recent banking and regulatory news.

5. **Medical and Scientific Advances** — Identify and briefly describe any recent biomedical or research-driven advancements related to cannabis or cannabinoids.

6. **Story Count** — State how many news articles were reviewed for this analysis.


Below are {len(subset)} articles:

{combined}
"""
    return prompt.strip()


def run_ollama_analysis(prompt, model):
    try:
        print("\n\U0001f9e0 Running sentiment analysis with Ollama...\n")
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if result.returncode != 0:
            print("❌ Ollama failed to run. Error:")
            print(result.stderr)
            return None

        return result.stdout.strip()

    except Exception as e:
        print(f"❌ Ollama subprocess error: {e}")
        return None

def save_report(text, path):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("# \U0001f9fe Cannabis News Sentiment Analysis\n\n")
            f.write(text)
        print(f"📄 Report saved to {path}")
    except Exception as e:
        print(f"❌ Failed to save report: {e}")

def main():
    df = load_news_data(CSV_PATH)
    if df.empty:
        return

    prompt = prepare_prompt(df)
    result = run_ollama_analysis(prompt, MODEL)

    if result:
        print("\n📈 Sentiment Analysis Result:\n")
        print(result)
        save_report(result, REPORT_PATH)

if __name__ == "__main__":
    main()
