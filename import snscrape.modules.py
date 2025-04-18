from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import csv

# Simple Nitter scraper using Selenium
BASE_URL = "https://nitter.net"
SEARCH_TERMS = [
    "Rafał Trzaskowski",
    "Sławomir Mentzen",
    "Karol Nawrocki",
    "Szymon Hołownia"
]

# Initialize the WebDriver (you might need to adjust the path to your driver)
# For example, for Chrome:
# options = webdriver.ChromeOptions()
# options.add_argument('--headless') # Run in headless mode (no browser window)
# driver = webdriver.Chrome(options=options)
driver = webdriver.Firefox() # Or any other browser driver you have installed

# Open a CSV file for writing
with open("nitter_selenium_data.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Search Term", "Username", "Tweet Text"])  # Write header row

    for term in SEARCH_TERMS:
        # Build search URL
        time.sleep(random.uniform(1, 2))
        query = term.replace(" ", "+")
        url = f"{BASE_URL}/search?f=tweets&q={query}"
        print(f"Searching for: {url}")

        try:
            # Fetch the page using Selenium
            driver.get(url)

            # Wait for the tweet elements to load (adjust timeout if needed)
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "timeline-item"))
            )

            # Find tweet blocks
            tweets = driver.find_elements(By.CLASS_NAME, "timeline-item")
            if not tweets:
                print(f"No tweets found for '{term}'.")
                continue

            # Extract data from each tweet
            for tweet in tweets:
                try:
                    username_element = tweet.find_element(By.CSS_SELECTOR, ".fullname")
                    tweet_text_element = tweet.find_element(By.CSS_SELECTOR, ".tweet-content")

                    username = username_element.text.strip()
                    tweet_text = tweet_text_element.text.strip()
                    writer.writerow([term, username, tweet_text])
                    print(f"  - User: {username}, Tweet: {tweet_text[:50]}...") # Print a snippet
                except Exception as e:
                    print(f"  - Error extracting data from a tweet: {e}")

        except Exception as e:
            print(f"Error fetching or processing {url}: {e}")

        # Polite delay between searches
        time.sleep(random.uniform(1, 2))

# Close the browser
driver.quit()

print("Data saved to nitter_selenium_data.csv")