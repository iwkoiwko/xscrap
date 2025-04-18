import tweepy
import pandas as pd

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAAbR0gEAAAAAfoxhT4QFFP6vqo45656EwXE1kKA%3DNgpTsW0eddxdCq9QPFrImSyf8xV131rVD7Iv7sADIi4kGPFrIv"
data_limit = "2025-03-25T00:00:00Z"

client = tweepy.Client(bearer_token=BEARER_TOKEN)


query = "Rafał Trzaskowski -is:retweet lang:pl"

response = client.search_recent_tweets(query=query, tweet_fields=["created_at", "author_id", "text"], start_time = data_limit)

tweets_data = []

for tweet in response.data:
    tweets_data.append({
        "author_id": tweet.author_id,
        "created_at": tweet.created_at,
        "text": tweet.text
    })


df = pd.DataFrame(tweets_data)
print(df.head())
df.to_csv("trzaskowski_csv")