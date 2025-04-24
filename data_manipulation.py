import pandas as pd
file = "nitter_selenium_data.csv"
df = pd.read_csv(file)
grouped_tweets = df.groupby('Username')['Tweet Text'].apply(list)
num_twt = df['Username'].value_counts()
grouped_tweets.to_csv("grouped_tweets.csv")
print(grouped_tweets)
#number of all tweets
print("number of tweets", sum(num_twt))

#number of tweets about each candidate
num_tweets_by_query = df['Search Term'].value_counts()
print("number of tweets about every candidate", num_tweets_by_query)




from transformers import pipeline


# Set up the sentiment classifier
classifier = pipeline("sentiment-analysis", model="papluca/xlm-roberta-base-polish-sentiment")

# Define the candidates to monitor
candidates = ['Rafał', 'Sławomir', 'Karol', 'Szymon']

# Store user-level support data
user_support = {}

for username, tweets in grouped_tweets.items():
    support = {cand: {'pos': 0, 'neg': 0, 'neu': 0} for cand in candidates}
    
    for tweet in tweets:
        for cand in candidates:
            if cand.lower() in tweet.lower():
                sentiment = classifier(tweet)[0]
                label = sentiment['label']
                
                if label == 'positive':
                    support[cand]['pos'] += 1
                elif label == 'negative':
                    support[cand]['neg'] += 1
                elif label == 'neutral':
                    support[cand]['neu'] += 1

    # Determine net sentiment score (positive - negative)
    sentiment_scores = {cand: (vals['pos'] - vals['neg']) for cand, vals in support.items()}
    top_candidate = max(sentiment_scores, key=sentiment_scores.get) if any(sentiment_scores.values()) else None
    
    user_support[username] = {
        'support': top_candidate,
        'sentiment_scores': sentiment_scores,
        'raw_counts': support
    }

# Convert results to a DataFrame for analysis or export
support_df = pd.DataFrame.from_dict(user_support, orient='index')
print(support_df)

# Save support analysis to file
support_df.to_csv("user_candidate_support_detailed.csv")
