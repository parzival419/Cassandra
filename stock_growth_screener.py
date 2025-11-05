import yfinance as yf
import pandas as pd
import numpy as np
import subprocess
import os

class GrowthStockAnalyzer:
    def __init__(self, symbols):
        self.symbols = symbols

    # -------------------------------------------------------------
    # Fetch data safely using yfinance with fallbacks
    # -------------------------------------------------------------
    def fetch_data(self):
        """Download financial and summary data for each symbol."""
        all_data = []

        for sym in self.symbols:
            print(f"📊 Fetching {sym}...")
            stock = yf.Ticker(sym)

            try:
                info = stock.info or {}
            except Exception as e:
                print(f"⚠️ Could not fetch info for {sym}: {e}")
                info = {}

            # Get available metrics or fallback
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            market_cap = info.get("marketCap")
            pe_ratio = info.get("trailingPE")
            revenue_growth = info.get("revenueGrowth")
            profit_margin = info.get("profitMargins")

            # --- fallback for missing price ---
            if not current_price:
                try:
                    hist = stock.history(period="5d")
                    if not hist.empty:
                        current_price = float(hist["Close"].iloc[-1])
                except Exception:
                    current_price = None

            all_data.append({
                "Symbol": sym,
                "CurrentPrice": current_price or 0.0,
                "MarketCap": market_cap or 0,
                "PE_Ratio": pe_ratio or 0,
                "RevenueGrowth(%)": round(revenue_growth * 100, 2) if revenue_growth else 0,
                "ProfitMargin(%)": round(profit_margin * 100, 2) if profit_margin else 0
            })

        df = pd.DataFrame(all_data)
        print("\n✅ Raw Data Collected:")
        print(df)
        df.to_csv("growth_candidates.csv", index=False)
        print("💾 Saved to growth_candidates.csv")
        return df

    # -------------------------------------------------------------
    # Apply basic growth filters
    # -------------------------------------------------------------
    def screen_for_growth(self, df):
        """Apply filters for cheap growth potential."""
        mask = (
            (df["CurrentPrice"].fillna(0) < 10) &
            (df["PE_Ratio"].fillna(0) < 30) &
            (df["RevenueGrowth(%)"].fillna(0) > 0) &
            (df["ProfitMargin(%)"].fillna(0) > 0)
        )

        screened = df[mask].copy()
        screened.to_csv("growth_screened.csv", index=False)
        print("\n Filtered Candidates:")
        print(screened if not screened.empty else "No stocks passed filters.")
        print(" Saved filtered list to growth_screened.csv")
        return screened

    # -------------------------------------------------------------
    # Generate Ollama AI summary
    # -------------------------------------------------------------
    def ollama_summary(self, df, model="llama2-uncensored"):
        """Generate growth potential summary with Ollama."""
        # If the filtered set is empty, use the raw data
        if df.empty:
            print(" No qualifying stocks found; using all raw data instead.")
            try:
                df = pd.read_csv("growth_candidates.csv")
            except FileNotFoundError:
                print(" No data found for Ollama summary.")
                return

        df_str = df.to_string(index=False)
        prompt = f"""
You are a financial analyst. Based on the following low-price stock data,
identify which tickers show the best growth potential, which appear risky,
and provide a short reasoning for each.

Data:
{df_str}
"""

        try:
            print("\n Generating summary with Ollama...\n")
            result = subprocess.run(
                ["ollama", "run", model],
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            print("📈 Ollama Analysis:\n")
            print(result.stdout)

            with open("growth_analysis.md", "w", encoding="utf-8") as f:
                f.write("# 🚀 Cheap Growth Stock Analysis\n\n")
                f.write(result.stdout)
            print("📝 Saved analysis to growth_analysis.md")

        except Exception as e:
            print(f"⚠️ Ollama analysis failed: {e}")


# -------------------------------------------------------------
# Main execution
# -------------------------------------------------------------
if __name__ == "__main__":
    # 👇 you can freely change these
    symbols = ["CURLF", "VRNOF", "TCNNF"]

    analyzer = GrowthStockAnalyzer(symbols)
    df = analyzer.fetch_data()
    screened = analyzer.screen_for_growth(df)
    analyzer.ollama_summary(screened)
