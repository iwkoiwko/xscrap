from ntscraper import Nitter
import time
import random as r
import pandas as pd
# Provide known good Nitter instance(s)
instances = ["https://nitter.net", "https://nitter.poast.org", "https://nitter.privacydev.net"]

# IMPORTANT: pass instances directly when creating the scraper
scraper = Nitter(instances=instances, skip_instance_check=True, log_level=1)

terms = ["Rafał Trzaskowski", "Sławomir Mentzen", "Karol Nawrocki", "Szymon Hołownia"]

if __name__ == "__main__":
    try:
        results = scraper.get_tweets(terms, mode='term')
        for term in terms:
            print(f"\nResults for '{term}':")
            for tweet in results[term]['tweets'][:5]:
                print(f"- @{tweet['user']['username']}: {tweet['text'][:100]}…")
            time.sleep(r.uniform(1, 2))
    except Exception as e:
        print(f"Error: {e}")
result.to_csv("wyniki.csv")