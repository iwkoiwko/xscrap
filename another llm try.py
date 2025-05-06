import pandas as pd
import re
import torch
from transformers import XLMRobertaTokenizer, XLMRobertaForSequenceClassification

def clean_text(text):
    # Konwertuj wszystko na string i usuń zbędne znaki
    text = str(text)
    text = re.sub(r"[\\\[\]'\"]", "", text)  # usuń \ [ ] ' "
    text = re.sub(r"\s+", " ", text)         # usuń wielokrotne spacje/nowe linie
    return text.strip()

file = "nitter_selenium_data.csv"
df = pd.read_csv(file)

grouped_tweets = df.groupby('Username')['Tweet Text'].apply(list)
num_twt = df['Username'].value_counts()

grouped_tweets.to_csv("grouped_tweets.csv")
print(grouped_tweets)

# number of all tweets
print("number of tweets", sum(num_twt))

# number of tweets about each candidate
num_tweets_by_query = df['Search Term'].value_counts()
print("number of tweets about every candidate", num_tweets_by_query)

def test():
    return print("ładowanie")

# Load model directly
# Note: For XLM-RoBERTa to act as a classifier, it needs to be fine-tuned on sentiment data
# Here we're assuming you have a fine-tuned model or you will fine-tune it
# If you need a pre-fine-tuned model, consider using: 'cardiffnlp/twitter-xlm-roberta-base-sentiment'
MODEL_NAME = "FacebookAI/xlm-roberta-large"  # Replace with fine-tuned model if available

tokenizer = XLMRobertaTokenizer.from_pretrained(MODEL_NAME)
model = XLMRobertaForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=3)
model.eval()  # Set model to evaluation mode

# Define the candidates to monitor
candidates = ['Rafał', 'Sławomir', 'Karol', 'Szymon','Adrian']

# Define function for sentiment prediction with truncation
def get_sentiment(text):
    # Add truncation=True to handle long texts
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Get predicted class
    predicted_class = torch.argmax(outputs.logits, dim=1).item()
    
    # Map class index to label (adjust based on your fine-tuned model's class mapping)
    id2label = {0: "negative", 1: "neutral", 2: "positive"}
    return {"label": id2label[predicted_class]}

# Store user-level support data
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
support_df.to_csv("user_candidate_support_detailed2.csv")