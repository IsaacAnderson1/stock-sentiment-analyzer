import streamlit as st
import pandas as pd
from transformers import pipeline
import snscrape.modules.twitter as sntwitter
from tqdm import tqdm

@st.cache_data
def fetch_tweets(ticker: str, limit: int = 100):
    query = f"${ticker} OR {ticker} lang:en -filter:retweets"
    tweets = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        if i >= limit:
            break
        tweets.append(tweet.content)
    return tweets

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

def main():
    st.title("📊 Stock Tweet Sentiment Analyzer")
    st.write("""
    Type in a **stock ticker** (like `AAPL`, `TSLA`, or `NVDA`) and get sentiment analysis from the
    latest tweets about it.  
    This uses **snscrape** to fetch tweets and a **Twitter-tuned RoBERTa model** for sentiment.
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
