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
    "Szymon Hołownia",
    "Adrian Zandberg"
]

options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)


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
        print(url)
        try:
            driver.get(url)
            print(f"Navigated to: {url}")
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "timeline-item"))
            )
            

            term_tweet_ids = set()
            last_height = driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scroll_attempts = 50  
            
            while scroll_attempts < max_scroll_attempts:

                for _ in range(5):
                    driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(0.3)

                try:
                    tweets = driver.find_elements(By.CLASS_NAME, "timeline-item")
                    print(f"Found {len(tweets)} tweets on page")
                    
                    new_tweets = 0
                    for tweet in tweets:
                        time.sleep(random.uniform(2, 3))  
                        try:
                     
                            tweet_id = tweet.get_attribute("data-tweet-id")
                            if not tweet_id: 
                                try:
                                    permalink = tweet.find_element(By.CSS_SELECTOR, ".tweet-link").get_attribute("href")
                                    tweet_id = permalink.split("/")[-1] if permalink else None
                                except:
                                    tweet_id = str(hash(tweet.text))  
                            
                            if tweet_id in term_tweet_ids:
                                time.sleep(random.uniform(0, 3))  
                                continue
                                
                            term_tweet_ids.add(tweet_id)
                            
                    
                            try:
                                username = tweet.find_element(By.CSS_SELECTOR, ".fullname").text.strip()
                                tweet_text = tweet.find_element(By.CSS_SELECTOR, ".tweet-content").text.strip()
                             
                                try:
                                    timestamp = tweet.find_element(By.CSS_SELECTOR, ".tweet-date a").get_attribute("title")
                                except:
                                    timestamp = "Unknown"
                                
                            
                                writer.writerow([term, username, tweet_text, timestamp, tweet_id])
                                csvfile.flush() 
                                new_tweets += 1
                                term_tweets += 1
                                total_tweets += 1
                                time.sleep(random.uniform(0, 3))  
                                
                            except (StaleElementReferenceException, NoSuchElementException) as e:
                                print(f"Error extracting data from tweet: {e}")
                                continue
                                
                        except Exception as e:
                            print(f"Error processing tweet: {e}")
                            continue
                    
                    print(f"Added {new_tweets} new tweets for '{term}'. Total for term: {term_tweets}")
                    
                 
                    if new_tweets == 0:
                        try:
                            load_more = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Load more')]"))
                            )
                            print("Clicking 'Load more'...")
                            driver.execute_script("arguments[0].click();", load_more)
                            time.sleep(2)  
                        except Exception as e:
                            print(f"No 'Load more' button found or not clickable: {e}")
                            break 
                    
                except Exception as e:
                    print(f"Error finding tweets: {e}")
                
              
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    scroll_attempts += 1
                    if scroll_attempts >= 3: 
                        try:
                     
                            load_more = driver.find_element(By.XPATH, "//a[contains(text(), 'Load more')]")
                            driver.execute_script("arguments[0].click();", load_more)
                            time.sleep(2)
                            scroll_attempts = 0  
                            time.sleep(random.uniform(2, 3))  
                        except:
                            print("Reached end of results - no more tweets to load")
                            break
                else:
                    scroll_attempts = 0  
                    last_height = new_height
            
            print(f"Completed search for '{term}'. Collected {term_tweets} tweets.")
            
        except Exception as e:
            print(f"Error processing search term '{term}': {e}")
        
        time.sleep(random.uniform(2, 3))  

driver.quit()
print(f"\nData collection complete. Total tweets collected: {total_tweets}")
print("Data saved to nitter_selenium_data.csv")
