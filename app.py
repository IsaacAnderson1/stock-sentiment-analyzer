import streamlit as st
import pandas as pd
import subprocess
from transformers import pipeline
from tqdm import tqdm

# --- Helper: Fetch tweets using snscrape CLI ---
@st.cache_data
def fetch_tweets(ticker: str, limit: int = 100):
    query = f"${ticker} OR {ticker} lang:en -filter:retweets"
    cmd = ["snscrape", "--max-results", str(limit), "twitter-search", query]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Each tweet text is on its own line
    tweets = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return tweets

# --- Helper: Analyze sentiment using pretrained model ---
@st.cache_data
def analyze_sentiment(tweets: list):
    sentiment_model = pipeline(
        "sentiment-analysis",
        model="cardiffnlp/twitter-roberta-base-sentiment-latest"
    )
    results = []
    for t in tqdm(tweets, desc="Analyzing tweets"):
        res = sentiment_model(t)[0]
        results.append(res)
    return pd.DataFrame(results)

# --- Streamlit app main ---
def main():
    st.title("📊 Stock Tweet Sentiment Analyzer")
    st.write("""
    Type a **stock ticker** (e.g. AAPL, TSLA, NVDA)  
    → Fetches latest tweets mentioning the ticker  
    → Runs a fine-tuned sentiment model  
    → Displays sentiment distribution + sample tweets
    """)

    ticker = st.text_input("Enter stock ticker:", "AAPL").upper().strip()
    limit = st.slider("Number of tweets", min_value=20, max_value=300, value=100, step=10)

    if st.button("Analyze Sentiment"):
        with st.spinner(f"Fetching tweets for {ticker}..."):
            tweets = fetch_tweets(ticker, limit)
        if not tweets:
            st.error("No tweets found. Try another ticker.")
            return

        with st.spinner("Running sentiment analysis..."):
            df = analyze_sentiment(tweets)

        st.success(f"✅ Completed analysis on {len(tweets)} tweets.")

        st.subheader("Sentiment Summary")
        counts = df['label'].value_counts(normalize=True) * 100
        st.bar_chart(counts)

        st.write("**Sentiment Distribution (%)**")
        st.dataframe(counts.round(2))

        st.write("**Average confidence:**", round(df['score'].mean(), 3))

        st.subheader("Sample of analyzed tweets")
        st.dataframe(pd.DataFrame({
            "Tweet": tweets,
            "Sentiment": df['label'],
            "Confidence": df['score'].round(3)
        }))

if __name__ == "__main__":
    main()
