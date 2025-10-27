import streamlit as st
import praw
import re  # Import the regular expression library

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

# ---- RELEVANCE/CONTEXT RULES ----
# Words that suggest the post is actually about finance/stocks
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

# ---- RELEVANCE CHECK FUNCTION ----
def is_post_relevant(text, ticker):
    text_lower = text.lower()
    
    # 1. Check if the ticker is actually in the text.
    # We use regex with \b (word boundary) to ensure "T" (for Ford) 
    # doesn't just match the letter in "THE".
    if not re.search(r'\b' + re.escape(ticker.lower()) + r'\b', text_lower):
        return False
        
    # 2. Check for at least one financial context word.
    if any(word in text_lower for word in financial_context_words):
        return True
        
    # 3. As a fallback, check if the ticker is cashtagged (e.g., $AAPL)
    if f'${ticker.lower()}' in text_lower:
        return True
        
    return False

# ---- MODIFIED FETCH FUNCTION (using Solution 1 logic) ----
def fetch_reddit_posts(ticker, limit=100):
    posts = []
    subreddit_names = "stocks+wallstreetbets+investing"
    subreddit = reddit.subreddit(subreddit_names)
    
    # We must fetch *more* than the limit, because we will filter some out.
    # Let's fetch 3x the limit to have a good chance of finding relevant posts.
    search_limit = limit * 3 

    for submission in subreddit.search(ticker, sort="new", limit=search_limit):
        full_text = submission.title + " " + submission.selftext
        
        # Here is the relevance filter!
        if is_post_relevant(full_text, ticker):
            posts.append(full_text)
        
        # Stop once we've collected enough *relevant* posts
        if len(posts) >= limit:
            break
            
    return posts

# ---- STREAMLIT UI ----
st.title("📈 Reddit Stock Sentiment Analyzer")

ticker = st.text_input("Enter stock ticker (e.g. AAPL, TSLA, NVDA):", "").upper()

if st.button("Analyze Sentiment"):
    if not ticker:
        st.warning("Please enter a ticker symbol.")
    else:
        st.info(f"Fetching and filtering Reddit posts mentioning **{ticker}** ...")
        posts = fetch_reddit_posts(ticker)

        if not posts:
            st.warning("No relevant posts found. Try another ticker.")
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
