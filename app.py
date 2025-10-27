import streamlit as st
import praw  # Reddit API wrapper
import re

# ---- CONFIGURE REDDIT API ----
# Create a Reddit app at https://www.reddit.com/prefs/apps
# and paste your credentials here
reddit = praw.Reddit(
    client_id="rR8y6HlQatpqsAi_rQ6RSg",
    client_secret="MfQGKDlHm8R6i0jAFRLEeGYViq-cfg",
    user_agent="StockSentimentApp/1.0"
)

# ---- BASIC SENTIMENT RULES ----
positive_words = ["buy", "bull", "up", "gain", "moon", "green", "profit", "undervalued", "strong"]
negative_words = ["sell", "bear", "down", "loss", "red", "crash", "overvalued", "weak"]

def get_sentiment(text):
    text = text.lower()
    pos = sum(word in text for word in positive_words)
    neg = sum(word in text for word in negative_words)
    if pos > neg:
        return 1
    elif neg > pos:
        return -1
    else:
        return 0

def fetch_reddit_posts(ticker, limit=100):
    posts = []
    for subreddit in ["stocks", "wallstreetbets", "investing"]:
        for submission in reddit.subreddit(subreddit).search(ticker, limit=limit):
            posts.append(submission.title + " " + submission.selftext)
    return posts[:limit]

# ---- STREAMLIT UI ----
st.title("📈 Reddit Stock Sentiment Analyzer")

ticker = st.text_input("Enter stock ticker (e.g. AAPL, TSLA, NVDA):", "").upper()

if st.button("Analyze Sentiment"):
    if not ticker:
        st.warning("Please enter a ticker symbol.")
    else:
        st.info(f"Fetching Reddit posts mentioning **{ticker}** ...")
        posts = fetch_reddit_posts(ticker)

        if not posts:
            st.warning("No posts found. Try another ticker.")
        else:
            sentiments = [get_sentiment(p) for p in posts]
            total_score = sum(sentiments)
            avg_score = total_score / len(posts)

            st.subheader("🔹 Sentiment Summary")
            st.write(f"Total Posts Analyzed: {len(posts)}")
            st.write(f"Overall Sentiment Score: {total_score}")
            st.write(f"Average Sentiment: {avg_score:.2f}")

            st.subheader("📝 Example Posts")
            for p in posts[:5]:
                s = get_sentiment(p)
                st.write(f"{'🟢' if s > 0 else '🔴' if s < 0 else '⚪'} {p[:300]}{'...' if len(p)>300 else ''}")
