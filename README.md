# Reddit Stock Sentiment Analyzer

A small Streamlit prototype that searches Reddit posts about a stock ticker using PRAW. It filters posts by ticker relevance, applies a keyword-based sentiment rule, and shows a summary with example posts.

The search covers r/stocks, r/wallstreetbets, and r/investing. You can include lower-confidence posts where the ticker appears only in the body.

## Run locally

1. Install dependencies with `pip install -r requirements.txt`.
2. Create a Reddit API application and set the `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` environment variables. Do not put credentials in source code or commit them.
3. Run `streamlit run app.py`.

This is a rule-based demo, not a trained machine-learning model or investment advice.
