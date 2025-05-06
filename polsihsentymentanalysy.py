import pandas as pd
import re
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def clean_text(text):
 
    text = str(text)
    text = re.sub(r"[\\\[\]'\"]", "", text)  
    text = re.sub(r"\s+", " ", text)         
    return text.strip()

file = "nitter_selenium_data.csv"
df = pd.read_csv(file)

grouped_tweets = df.groupby('Username')['Tweet Text'].apply(list)
num_twt = df['Username'].value_counts()

grouped_tweets.to_csv("grouped_tweets.csv")
print(grouped_tweets)

total_tweets = sum(num_twt)
print("number of tweets:", total_tweets)


num_tweets_by_query = df['Search Term'].value_counts()
print("number of tweets about every candidate:", num_tweets_by_query)


basic_info = pd.DataFrame({
    'Total_Tweets': [total_tweets],
    'Candidate_Count': [len(num_tweets_by_query)]
})

for candidate, count in num_tweets_by_query.items():
    basic_info[f'Tweets_{candidate}'] = count


basic_info.to_csv("tweet_summary_stats.csv", index=False)

def test():
    return print("ładowanie")


tokenizer = AutoTokenizer.from_pretrained("eevvgg/bert-polish-sentiment-politics")
model = AutoModelForSequenceClassification.from_pretrained("eevvgg/bert-polish-sentiment-politics")
model.eval()  

candidates = ['Rafał', 'Sławomir', 'Karol', 'Szymon','Adrian']


def get_sentiment(text):
   
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    

    predicted_class = torch.argmax(outputs.logits, dim=1).item()
    

    id2label = {0: "negative", 1: "neutral", 2: "positive"}
    return {"label": id2label[predicted_class]}

user_support = {}

for username, tweets in grouped_tweets.items():
    support = {cand: {'pos': 0, 'neg': 0, 'neu': 0} for cand in candidates}
    test()
    for tweet in tweets:
        clean_tweet = clean_text(tweet)
        for cand in candidates:
            clean_cand = clean_text(cand)
            if clean_cand.lower() in clean_tweet.lower():
                test()
                try:
                    sentiment = get_sentiment(clean_tweet)
                    label = sentiment['label']
                    
                    if label == "positive":
                        support[cand]['pos'] += 1
                    elif label == "negative":
                        support[cand]['neg'] += 1
                    elif label == "neutral":
                        support[cand]['neu'] += 1
                except Exception as e:
                    print(f"Error processing tweet for {username} about {cand}: {str(e)[:100]}...")
                    continue

 
    sentiment_scores = {cand: (vals['pos'] - vals['neg']) for cand, vals in support.items()}
    top_candidate = max(sentiment_scores, key=sentiment_scores.get) if any(sentiment_scores.values()) else None
    
    user_support[username] = {
        'support': top_candidate,
        'sentiment_scores': sentiment_scores,
        'raw_counts': support
    }

support_df = pd.DataFrame.from_dict(user_support, orient='index')
print(support_df)


support_df.to_csv("user_candidate_support_detailed.csv")