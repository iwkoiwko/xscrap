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

# Simple user agents list
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
]

options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={random.choice(user_agents)}")  # Random user agent
options.add_argument("--disable-blink-features=AutomationControlled")  # Hide automation flags
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

# Modify CDP Parameters to mask webdriver usage
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    """
})

all_collected_tweets = set()
total_tweets = 0

with open("nitter_selenium_data.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Search Term", "Username", "Tweet Text", "Timestamp", "Tweet ID"])

    for term in SEARCH_TERMS:
        term_tweets = 0
        print(f"\nSearching for: {term}")
        time.sleep(random.uniform(2, 4))  # More human-like delay
        query = term.replace(" ", "+")
        url = f"{BASE_URL}/search?f=tweets&q={query}&since=2025-03-24&until=&near="
        print(url)
        try:
            driver.get(url)
            print(f"Navigated to: {url}")
            
            # Add a random tiny movement to the mouse (more human-like)
            driver.execute_script(f"window.scrollBy({random.randint(1, 5)}, {random.randint(1, 5)});")
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "timeline-item"))
            )
            
            term_tweet_ids = set()
            last_height = driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scroll_attempts = 50  
            
            while scroll_attempts < max_scroll_attempts:
                # More human-like scrolling with variable speed
                for _ in range(random.randint(3, 6)):
                    scroll_amount = random.randint(300, 700)
                    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                    time.sleep(random.uniform(0.2, 0.5))  # Variable delay

                try:
                    tweets = driver.find_elements(By.CLASS_NAME, "timeline-item")
                    print(f"Found {len(tweets)} tweets on page")
                    
                    new_tweets = 0
                    for tweet in tweets:
                        # Less predictable delay
                        time.sleep(random.uniform(1.5, 3.5))  
                        try:
                            tweet_id = tweet.get_attribute("data-tweet-id")
                            if not tweet_id: 
                                try:
                                    permalink = tweet.find_element(By.CSS_SELECTOR, ".tweet-link").get_attribute("href")
                                    tweet_id = permalink.split("/")[-1] if permalink else None
                                except:
                                    tweet_id = str(hash(tweet.text))  
                            
                            if tweet_id in term_tweet_ids:
                                time.sleep(random.uniform(0, 2))  
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
                                time.sleep(random.uniform(0, 2))  
                                
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
                            # More human-like clicking
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more)
                            time.sleep(random.uniform(0.5, 1.5))
                            driver.execute_script("arguments[0].click();", load_more)
                            time.sleep(random.uniform(1.5, 3))
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
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more)
                            time.sleep(random.uniform(0.5, 1.5))
                            driver.execute_script("arguments[0].click();", load_more)
                            time.sleep(random.uniform(1.5, 3))
                            scroll_attempts = 0
                        except:
                            print("Reached end of results - no more tweets to load")
                            break
                else:
                    scroll_attempts = 0  
                    last_height = new_height
            
            print(f"Completed search for '{term}'. Collected {term_tweets} tweets.")
            
        except Exception as e:
            print(f"Error processing search term '{term}': {e}")
        
        # Random delay between search terms (more human-like)
        time.sleep(random.uniform(3, 6))

driver.quit()
print(f"\nData collection complete. Total tweets collected: {total_tweets}")
print("Data saved to nitter_selenium_data.csv")