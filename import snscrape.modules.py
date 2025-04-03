import requests
from bs4 import BeautifulSoup

NITTER_INSTANCE = "https://nitter.net"

search_query = '"Rafał Trzaskowski" since:2025-03-24'
url = f"{NITTER_INSTANCE}/search?q={search_query}&f=tweets"

headers = {"User-Agent": "Mozilla/5.0"}


response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("wejscie do if")
    soup = BeautifulSoup(response.text, "html.parser")
    tweets = soup.find_all("div", class_="tweet-link")

    for i, tweet in enumerate(tweets[:5]):  
        print("wejscie do petli")
        print(f"Tweet {i+1}: {tweet.text.strip()}\n")
else:
    print("Failed to fetch tweets. Try a different Nitter instance.")
