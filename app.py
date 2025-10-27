import streamlit as st
import praw
import re

# ---- CONFIGURE REDDIT API ----
# (Your credentials here)
reddit = praw.Reddit(
    client_id="rR8y6HlQatpqsAi_rQ6RSg",
    client_secret="MfQGKDlHm8R6i0jAFRLEeGYViq-cfg",
    user_agent="StockSentimentApp/1.0"
)

# ---- SENTIMENT & CONTEXT RULES ----
positive_words = ["buy", "bull", "up", "gain", "moon", "green", "profit", "undervalued", "strong"]
negative_words = ["sell", "bear", "down", "loss", "red", "crash", "overvalued", "weak"]
financial_context_words = [
    "stock", "stocks", "shares", "market", "trading", "invest", "investing",
    "earnings", "dividend", "p/e", "portfolio", "bullish", "bearish",
    "buy", "sell", "hold", "options", "calls", "puts", "gains", "loss",
    "percent", "yolo", "dd", "ATH", "dip", "diamond hands"
]

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

# ---- NEW: RELEVANCE FUNCTION (with Confidence Score) ----
def get_post_relevance(submission, ticker):
    """
    Analyzes a post and returns a confidence score.
    2 = High (Cashtag)
    1 = Medium (Ticker in Title)
    0 = Low (Ticker in Body + Context)
    -1 = Irrelevant
    """
    title_lower = submission.title.lower()
    body_lower = submission.selftext.lower()
    full_text_lower = title_lower + " " + body_lower
    ticker_lower = ticker.lower()

    # Regex for ticker: \bTICKER\b (whole word)
    ticker_regex = r'\b' + re.escape(ticker_lower) + r'\b'
    # Regex for cashtag: $TICKER
    cashtag_regex = r'\$' + re.escape(ticker_lower) + r'(\b|$)'

    # 1. High Confidence: Cashtag found anywhere
    if re.search(cashtag_regex, full_text_lower):
        return 2

    # 2. Medium Confidence: Ticker found in title
    if re.search(ticker_regex, title_lower):
        return 1
        
    # 3. Low Confidence: Ticker in body + financial context
    if re.search(ticker_regex, body_lower):
        if any(word in full_text_lower for word in financial_context_words):
            return 0  # Low confidence
            
    return -1 # Irrelevant

# ---- MODIFIED FETCH FUNCTION ----
def fetch_reddit_posts(ticker, limit=100, min_confidence=1):
    posts = []
    subreddit_names = "stocks+wallstreetbets+investing"
    subreddit = reddit.subreddit(subreddit_names)
    search_limit = limit * 5  # Search 5x more posts to find enough relevant ones

    for submission in subreddit.search(ticker, sort="new", limit=search_limit):
        
        relevance = get_post_relevance(submission, ticker)
        
        # Filter based on the minimum confidence level
        if relevance >= min_confidence:
            full_text = submission.title + " " + submission.selftext
            # Store the post and its relevance for sorting
            posts.append({'text': full_text, 'relevance': relevance})
        
        # Stop if we hit our limit, but only check every so often
        if len(posts) >= limit:
            break
            
    # Sort by relevance (highest first)
    posts.sort(key=lambda x: x['relevance'], reverse=True)
    
    # Return just the text, up to the limit
    return [p['text'] for p in posts[:limit]]

# ---- STREAMLIT UI (with new checkbox) ----
st.title("📈 Reddit Stock Sentiment Analyzer")

ticker = st.text_input("Enter stock ticker (e.g. AAPL, TSLA, NVDA):", "").upper()

# NEW: Add the checkbox
include_body_mentions = st.checkbox("Include lower-confidence (body-only) mentions")

if st.button("Analyze Sentiment"):
    if not ticker:
        st.warning("Please enter a ticker symbol.")
    else:
        # Set the confidence level based on the checkbox
        # Default (unchecked) is 1, so it only gets Title/Cashtag posts
        min_confidence = 0 if include_body_mentions else 1
        
        st.info(f"Fetching and filtering Reddit posts for **{ticker}** ...")
        posts = fetch_reddit_posts(ticker, limit=100, min_confidence=min_confidence)

        if not posts:
            st.warning("No relevant posts found. Try another ticker or check the box above.")
        else:
            sentiments = [get_sentiment(p) for p in posts]
            total_score = sum(sentiments)
            avg_score = total_score / len(posts)

            st.subheader("🔹 Sentiment Summary")
            st.write(f"Total Relevant Posts Analyzed: {len(posts)}")
            st.write(f"Overall Sentiment Score: {total_score}")
            st.write(f"Average Sentiment: {avg_score:.2f}")

            st.subheader("📝 Example Posts")
            for p in posts[:5]:
                s = get_sentiment(p)
                st.write(f"{'🟢' if s > 0 else '🔴' if s < 0 else '⚪'} {p[:300]}{'...' if len(p)>300 else ''}")
