from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import random
import csv
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

BASE_URL = "https://nitter.net"
SEARCH_TERMS = [
    "Rafał Trzaskowski",
    "Sławomir Mentzen",
    "Karol Nawrocki",
    "Szymon Hołownia"
]

# Initialize the webdriver with options for better performance
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

# Store all collected tweets to avoid duplicates
all_collected_tweets = set()
total_tweets = 0

with open("nitter_selenium_data.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Search Term", "Username", "Tweet Text", "Timestamp", "Tweet ID"])

    for term in SEARCH_TERMS:
        term_tweets = 0
        print(f"\nSearching for: {term}")
        time.sleep(random.uniform(1, 2))
        query = term.replace(" ", "+")
        url = f"{BASE_URL}/search?f=tweets&q={query}&since=2025-03-24&until=&near="
        
        try:
            driver.get(url)
            print(f"Navigated to: {url}")
            
            # Initial wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "timeline-item"))
            )
            
            # Track seen tweet IDs for this search term
            term_tweet_ids = set()
            last_height = driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scroll_attempts = 50  # Limit scrolling attempts
            
            while scroll_attempts < max_scroll_attempts:
                # Scroll down in smaller increments for better tweet loading
                for _ in range(5):
                    driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(0.3)
                
                # Process visible tweets after scrolling
                try:
                    tweets = driver.find_elements(By.CLASS_NAME, "timeline-item")
                    print(f"Found {len(tweets)} tweets on page")
                    
                    new_tweets = 0
                    for tweet in tweets:
                        try:
                            # Try to extract tweet ID from the element
                            tweet_id = tweet.get_attribute("data-tweet-id")
                            if not tweet_id:  # If no direct ID, try getting from permalink
                                try:
                                    permalink = tweet.find_element(By.CSS_SELECTOR, ".tweet-link").get_attribute("href")
                                    tweet_id = permalink.split("/")[-1] if permalink else None
                                except:
                                    tweet_id = str(hash(tweet.text))  # Fallback to hash of text
                            
                            # Skip if we've seen this tweet already
                            if tweet_id in term_tweet_ids:
                                continue
                                
                            term_tweet_ids.add(tweet_id)
                            
                            # Extract tweet data
                            try:
                                username = tweet.find_element(By.CSS_SELECTOR, ".fullname").text.strip()
                                tweet_text = tweet.find_element(By.CSS_SELECTOR, ".tweet-content").text.strip()
                                
                                # Also try to get timestamp if available
                                try:
                                    timestamp = tweet.find_element(By.CSS_SELECTOR, ".tweet-date a").get_attribute("title")
                                except:
                                    timestamp = "Unknown"
                                
                                # Write to CSV
                                writer.writerow([term, username, tweet_text, timestamp, tweet_id])
                                csvfile.flush()  # Force write to disk
                                new_tweets += 1
                                term_tweets += 1
                                total_tweets += 1
                                
                            except (StaleElementReferenceException, NoSuchElementException) as e:
                                print(f"Error extracting data from tweet: {e}")
                                continue
                                
                        except Exception as e:
                            print(f"Error processing tweet: {e}")
                            continue
                    
                    print(f"Added {new_tweets} new tweets for '{term}'. Total for term: {term_tweets}")
                    
                    # If we didn't find any new tweets, try clicking "Load more" or break
                    if new_tweets == 0:
                        try:
                            load_more = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Load more')]"))
                            )
                            print("Clicking 'Load more'...")
                            driver.execute_script("arguments[0].click();", load_more)
                            time.sleep(2)  # Wait for new content
                        except Exception as e:
                            print(f"No 'Load more' button found or not clickable: {e}")
                            break  # Exit the loop if we can't load more
                    
                except Exception as e:
                    print(f"Error finding tweets: {e}")
                
                # Check if we've scrolled to the bottom
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    scroll_attempts += 1
                    if scroll_attempts >= 3:  # If height hasn't changed for 3 attempts
                        try:
                            # Try clicking "Load more" one more time
                            load_more = driver.find_element(By.XPATH, "//a[contains(text(), 'Load more')]")
                            driver.execute_script("arguments[0].click();", load_more)
                            time.sleep(2)
                            scroll_attempts = 0  # Reset counter
                        except:
                            print("Reached end of results - no more tweets to load")
                            break
                else:
                    scroll_attempts = 0  # Reset counter if page height changes
                    last_height = new_height
            
            print(f"Completed search for '{term}'. Collected {term_tweets} tweets.")
            
        except Exception as e:
            print(f"Error processing search term '{term}': {e}")
        
        time.sleep(random.uniform(2, 3))  # Pause between search terms

driver.quit()
print(f"\nData collection complete. Total tweets collected: {total_tweets}")
print("Data saved to nitter_selenium_data.csv")
