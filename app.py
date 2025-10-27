import streamlit as st
import pandas as pd
import subprocess
import re

# --- Simple keyword lists ---
POSITIVE_WORDS = [
    "good", "great", "amazing", "awesome", "bullish", "love",
    "profit", "gain", "up", "strong", "buy", "moon", "pump"
]
NEGATIVE_WORDS = [
    "bad", "terrible", "awful", "bearish", "hate", "loss",
    "down", "weak", "sell", "crash", "dump"
]

# --- Helper: Fetch tweets using snscrape CLI ---
@st.cache_data
def fetch_tweets(ticker: str, limit: int = 100):
    query = f"${ticker} OR {ticker} lang:en -filter:retweets"
    cmd = ["snscrape", "--max-results", str(limit), "twitter-search", query]
    result = subprocess.run(cmd, capture_output=True, text=True)

    tweets = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return tweets

# --- Helper: Basic sentiment scoring ---
def get_sentiment_score(text: str) -> int:
    text = text.lower()
    score = 0
    for w in POSITIVE_WORDS:
        if re.search(rf"\b{w}\b", text):
            score += 1
    for w in NEGATIVE_WORDS:
        if re.search(rf"\b{w}\b", text):
            score -= 1
    return score

def analyze_sentiment(tweets):
    results = []
    for t in tweets:
        score = get_sentiment_score(t)
        label = "positive" if score > 0 else "negative" if score < 0 else "neutral"
        results.append({"tweet": t, "score": score, "label": label})
    return pd.DataFrame(results)

# --- Streamlit UI ---
def main():
    st.title("📊 Simple Stock Tweet Sentiment Analyzer")
    st.write("""
    Type a **stock ticker** (e.g. AAPL, TSLA, NVDA).  
    This app fetches recent tweets mentioning that ticker,  
    checks for positive/negative keywords, and assigns +1 or -1 to each tweet.
    """)

    ticker = st.text_input("Enter stock ticker:", "AAPL").upper().strip()
    limit = st.slider("Number of tweets", min_value=20, max_value=300, value=100, step=10)

    if st.button("Analyze Sentiment"):
        with st.spinner(f"Fetching tweets for {ticker}..."):
            tweets = fetch_tweets(ticker, limit)

        if not tweets:
            st.error("No tweets found. Try another ticker.")
            return

        with st.spinner("Analyzing sentiment..."):
            df = analyze_sentiment(tweets)

        # Summary
        total_score = df["score"].sum()
        pos_count = (df["score"] > 0).sum()
        neg_count = (df["score"] < 0).sum()
        neu_count = (df["score"] == 0).sum()

        st.success(f"✅ Completed analysis on {len(tweets)} tweets.")

        st.subheader("Sentiment Summary")
        st.write(f"**Overall Sentiment Score:** {total_score}")
        st.write(f"👍 Positive tweets: {pos_count}")
        st.write(f"👎 Negative tweets: {neg_count}")
        st.write(f"😐 Neutral tweets: {neu_count}")

        chart_data = pd.DataFrame({
            "Sentiment": ["Positive", "Negative", "Neutral"],
            "Count": [pos_count, neg_count, neu_count],
        })
        st.bar_chart(chart_data.set_index("Sentiment"))

        st.subheader("Sample of analyzed tweets")
        st.dataframe(df[["tweet", "label", "score"]])

if __name__ == "__main__":
    main()
