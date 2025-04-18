import twint
import pandas as pd
from datetime import datetime

class TwintScraper:
    def __init__(self, limit=100, hide_output=True):
        self.limit = limit
        self.hide_output = hide_output

    def fetch_tweets(self, term):
        """
        Fetch tweets for a given search term using Twint and return a DataFrame.
        """
        c = twint.Config()
        c.Search = term
        c.Limit = self.limit
        c.Pandas = True
        c.Hide_output = self.hide_output

        # Run the search
        twint.run.Search(c)

        # Retrieve the DataFrame
        df = twint.storage.panda.Tweets_df.copy()
        df['search_term'] = term
        # Select and rename relevant columns
        cols = [
            'search_term', 'id', 'username', 'name', 'date', 'time',
            'tweet', 'url', 'retweets_count', 'replies_count', 'likes_count'
        ]
        return df[cols]

    def scrape_terms(self, terms):
        """
        Loop through a list of terms and concatenate results.
        """
        frames = []
        for term in terms:
            print(f"Fetching tweets for: {term}")
            try:
                df = self.fetch_tweets(term)
                frames.append(df)
            except Exception as e:
                print(f"Error fetching for '{term}': {e}")
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


if __name__ == "__main__":
    # Define your search terms
    terms = [
        "Rafał Trzaskowski",
        "Sławomir Mentzen",
        "Karol Nawrocki",
        "Szymon Hołownia"
    ]

    # Initialize scraper
    scraper = TwintScraper(limit=50)

    # Scrape all terms
    result_df = scraper.scrape_terms(terms)

    if result_df.empty:
        print("No tweets found.")
    else:
        print(f"Fetched a total of {len(result_df)} tweets.")
        print(result_df.head())

        # Save to CSV
        filename = f"tweets_twint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        result_df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Results saved to: {filename}")
