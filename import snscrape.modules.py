import requests
from bs4 import BeautifulSoup

NITTER_INSTANCE = "https://nitter.net"

query = '%22Rafa%C5%82+Trzaskowski%22+since%3A2025-03-24'
url = f"{NITTER_INSTANCE}/search?f=tweets&q={query}"
print(f"zbieram tweety dla linku: "+url)
headers = {"User-Agent": "Mozilla/5.0"}


response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("wejscie do if")
    soup = BeautifulSoup(response.text, "html.parser")
    tweets = soup.find_all("div", class_="timeline-item")

    for i, tweet in enumerate(tweets[:5]):  
        print("wejscie do petli")
        print(f"Tweet {i+1}: {tweet.text.strip()}\n")

