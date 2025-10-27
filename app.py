import streamlit as st
import praw
import re
from transformers import pipeline  # <-- Import pipeline

# ---- AI Model Setup ----
# This uses @st.cache_resource to load the model only once.
@st.cache_resource
def load_classifier():
    st.info("Loading AI relevance model (this happens once)...")
    # Load a model trained for Natural Language Inference
    return pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-3")

classifier = load_classifier()

# (Rest of your setup: reddit, positive/negative words, get_sentiment)

# ---- MODIFIED: AI-Powered Fetch Function ----
def fetch_reddit_posts(ticker, limit=100):
    subreddit_names = "stocks+wallstreetbets+investing"
    subreddit = reddit.subreddit(subreddit_names)
    search_limit = limit * 3  # Fetch more to filter

    # The labels we will classify each post against
    candidate_labels = ["about stock market investing", "not about stocks"]

    texts_to_check = []
    original_posts = []

    # 1. Gather posts from Reddit
    for submission in subreddit.search(ticker, sort="new", limit=search_limit):
        full_text = submission.title + " " + submission.selftext
        # Truncate text for the model (models have a size limit)
        texts_to_check.append(full_text[:512]) 
        original_posts.append(full_text)

    if not texts_to_check:
        return []

    # 2. Classify all posts in one batch (this is the slow "AI" part)
    results = classifier(texts_to_check, candidate_labels)

    # 3. Filter the posts based on the AI's classification
    relevant_posts = []
    for original_text, result in zip(original_posts, results):
        # Check if the AI's top-scoring label is the one we want
        if result['labels'][0] == "about stock market investing":
            relevant_posts.append(original_text)

        if len(relevant_posts) >= limit:
            break

    return relevant_posts

# (Rest of your Streamlit UI code...)
