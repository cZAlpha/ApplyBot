import csv
import os
import argparse
from urllib.parse import urlparse
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import random
import math
import time
import re
import pandas as pd
import json
import glob



class JobScraper:
   def __init__(self, config=None, headless=False):
      self.config = config
      self.user_agents = [
         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:131.0) Gecko/20100101 Firefox/131.0",
         "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0", 
         "Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
      ]
      self.setup_driver()
      
      # Statistical tracking variables
      self.xpath_hits = {} # Object to hold the element_name -> [how_many_hits_xpath_1, ...] | Basically: An object to keep track of what xpaths are hitting the most for what elements being scraped for. This can be used to better curate the scraping of info. from job listings
      self.critical_element_scrape_fails = 0 # These indicate that XPaths MUST be changed to adjust for differing situations
      self.non_critical_element_scrape_fails = 0 # These indicate, if higher than should be expected, that XPaths likely need to be adjusted
   
   # Old version
   # def setup_driver(self, headless):
   #    """Setup Firefox driver with options"""
   #    firefox_options = Options()
      
   #    # Enhanced anti-detection settings
   #    firefox_options.set_preference("dom.webdriver.enabled", False)
   #    firefox_options.set_preference("useAutomationExtension", False)
   #    firefox_options.set_preference("privacy.trackingprotection.enabled", False)
   #    firefox_options.set_preference("privacy.resistFingerprinting", False)  # Disable resistFingerprinting for consistency
   #    firefox_options.set_preference("privacy.clearOnShutdown.offlineApps", False)
   #    firefox_options.set_preference("privacy.clearOnShutdown.passwords", False)
   #    firefox_options.set_preference("privacy.clearOnShutdown.siteSettings", False)
   #    firefox_options.set_preference("browser.cache.disk.enable", False)
   #    firefox_options.set_preference("browser.cache.memory.enable", False)
   #    firefox_options.set_preference("browser.sessionstore.resume_from_crash", False)
      
   #    # More realistic user profile
   #    firefox_options.set_preference("browser.startup.homepage", "about:blank")
   #    firefox_options.set_preference("startup.homepage_welcome_url", "about:blank")
   #    firefox_options.set_preference("startup.homepage_welcome_url.additional", "about:blank")
      
   #    # Use a more realistic window size
   #    firefox_options.add_argument("--width=1920")
   #    firefox_options.add_argument("--height=1080")
      
   #    if headless:
   #       firefox_options.add_argument("--headless")
      
   #    # Set user agent after all other preferences
   #    firefox_options.set_preference("general.useragent.override", random.choice(self.user_agents))
      
   #    try:
   #       self.driver = webdriver.Firefox(options=firefox_options)
   #       self.driver.set_page_load_timeout(30)
         
   #       # Additional JavaScript evasion
   #       self.driver.execute_script("""
   #             Object.defineProperty(navigator, 'webdriver', {
   #                get: () => undefined,
   #             });
   #             Object.defineProperty(navigator, 'plugins', {
   #                get: () => [1, 2, 3, 4, 5],
   #             });
   #             Object.defineProperty(navigator, 'languages', {
   #                get: () => ['en-US', 'en'],
   #             });
   #       """)
         
   #    except WebDriverException as e:
   #       print(f"Error setting up Firefox driver: {e}")
   #       raise
   
   # START - Stealth
   def human_mouse_movement(self, start_element, end_element):
      """Simulate human-like mouse movement between elements"""
      try:
         # Get element positions
         start_loc = start_element.location
         end_loc = end_element.location
         
         # Generate curved path using Bezier
         control_x = (start_loc['x'] + end_loc['x']) / 2 + random.randint(-50, 50)
         control_y = (start_loc['y'] + end_loc['y']) / 2 + random.randint(-50, 50)
         
         # Move through curve points
         for t in [i/10 for i in range(1, 11)]:
            x = (1-t)**2 * start_loc['x'] + 2*(1-t)*t * control_x + t**2 * end_loc['x']
            y = (1-t)**2 * start_loc['y'] + 2*(1-t)*t * control_y + t**2 * end_loc['y']
            
            # Add randomness to movement
            x += random.randint(-2, 2)
            y += random.randint(-2, 2)
            
            self.driver.execute_script(f"window.mouseX = {x}; window.mouseY = {y};")
            time.sleep(random.uniform(0.01, 0.03))
            
      except Exception as e:
         type_text(f"Mouse movement failed: {e}")
   
   def human_scroll(self, scroll_amount=None):
      """Simulate human-like scrolling"""
      if scroll_amount is None:
         scroll_amount = random.randint(200, 800)
      
      # Scroll in chunks with varied speed
      chunks = random.randint(3, 8)
      chunk_size = scroll_amount / chunks
      
      for i in range(chunks):
         # Vary scroll speed and direction slightly
         current_chunk = chunk_size * random.uniform(0.8, 1.2)
         self.driver.execute_script(f"window.scrollBy(0, {current_chunk});")
         
         # Random pauses between scrolls
         time.sleep(random.uniform(0.1, 0.4))
      
      # Sometimes scroll back a bit
      if random.random() > 0.7:
         time.sleep(random.uniform(0.5, 1.5))
         back_scroll = random.randint(50, 200)
         self.driver.execute_script(f"window.scrollBy(0, -{back_scroll});")
   
   def human_typing(self, element, text):
      """Simulate human-like typing with variable speed"""
      for char in text:
         element.send_keys(char)
         # Variable typing speed
         time.sleep(random.uniform(0.08, 0.25))
         
         # Occasional pauses like a human
         if random.random() > 0.95:
               time.sleep(random.uniform(0.5, 1.2))
   
   def random_behavior(self):
      """Perform random human-like behaviors"""
      behaviors = [
         lambda: self.human_scroll(random.randint(100, 400)),
         lambda: time.sleep(random.uniform(1, 3)),
         lambda: self.driver.execute_script("window.scrollBy(0, -100);"),
      ]
      
      # Perform 1-3 random behaviors
      for _ in range(random.randint(1, 3)):
         random.choice(behaviors)()
         time.sleep(random.uniform(0.5, 1.5))
   
   def human_delay(self):
      """Random delay between actions"""
      time.sleep(random.uniform(1.5, 4.0))
   # STOP - Stealth
   
   # START - Statistics
   def _track_xpath_hit(self, element_name, xpath_index, xpath_string):
      """Track which XPaths are successful for which elements | Statistical tracking function"""
      # Load current statistics from file
      stats = self._load_xpath_stats_from_file()
      
      if element_name not in stats:
         stats[element_name] = {}
      
      # Use a simplified key for the XPath (just the index or a hash)
      xpath_key = f"xpath_{xpath_index}"  # or use: hashlib.md5(xpath_string.encode()).hexdigest()[:8]
      
      if xpath_key not in stats[element_name]:
         stats[element_name][xpath_key] = {
               'count': 0,
               'xpath': xpath_string,
               'index': xpath_index
         }
      
      stats[element_name][xpath_key]['count'] += 1
      
      # Save updated statistics back to file
      self._save_xpath_stats_to_file(stats)
   
   def get_xpath_statistics(self):
      """Print out XPath hit statistics"""
      stats = self._load_xpath_stats_from_file()
      
      type_text("XPATH HIT STATISTICS")
      
      for element_name, xpaths in stats.items():
         type_text(f"\n{element_name}:")
         
         # Sort by count descending
         sorted_xpaths = sorted(xpaths.items(), key=lambda x: x[1]['count'], reverse=True)
         
         for xpath_key, data in sorted_xpaths:
               type_text(f"  XPath #{data['index']+1}: {data['count']} hits")
               type_text(f"    {data['xpath']}")
   
   def get_optimized_xpaths(self):
      """Get optimized XPath lists based on hit statistics"""
      stats = self._load_xpath_stats_from_file()
      optimized = {}
      
      for element_name, xpaths in stats.items():
         # Sort by hit count descending
         sorted_xpaths = sorted(xpaths.items(), key=lambda x: x[1]['count'], reverse=True)
         
         # Create optimized list maintaining original XPath objects
         optimized[element_name] = [data['xpath'] for _, data in sorted_xpaths]
      
      return optimized
   
   def save_xpath_statistics(self, filename="xpath_stats.json"):
      """Save XPath statistics to a file - kept for backward compatibility"""
      stats = self._load_xpath_stats_from_file()
      self._save_xpath_stats_to_file(stats, filename)
      type_text(f"XPath statistics saved to {filename}")
   
   def load_xpath_statistics(self, filename="xpath_stats.json"):
      """Load XPath statistics from a file - kept for backward compatibility"""
      try:
         with open(filename, 'r') as f:
               stats = json.load(f)
         
         # Update internal variable for compatibility
         self.xpath_hits = stats
         type_text(f"XPath statistics loaded from {filename}")
      except FileNotFoundError:
         type_text(f"No existing XPath statistics file found at {filename}")
      except Exception as e:
         type_text(f"Error loading XPath statistics: {e}")
   
   def _load_xpath_stats_from_file(self, filename="xpath_stats.json"):
      """Internal method to load statistics from file"""
      try:
         with open(filename, 'r') as f:
               return json.load(f)
      except FileNotFoundError:
         return {}  # Return empty dict if file doesn't exist
      except Exception as e:
         type_text(f"Error loading XPath statistics from file: {e}")
         return {}
   
   def _save_xpath_stats_to_file(self, stats, filename="xpath_stats.json"):
      """Internal method to save statistics to file"""
      try:
         with open(filename, 'w') as f:
               json.dump(stats, f, indent=2)
      except Exception as e:
         type_text(f"Error saving XPath statistics to file: {e}")
   
   def get_element_scraping_statistics(self):
      type_text("ELEMENT SCRAPING FAILURES")
      type_text("")
      if (self.critical_element_scrape_fails + self.non_critical_element_scrape_fails <= 0): # If no element scraping failures occurred
         type_text("No element scraping failures occurred! Woohoo!")
      else:
         type_text("Critical Element Scraping Failures: " + str(self.critical_element_scrape_fails)) # Number of times where a critical scraping element failed to be scraped
         type_text("Non-Critical Element Scraping Failures: " + str(self.non_critical_element_scrape_fails)) # Number of times where a non-critical scraping element failed to be scraped
   # STOP - Statistics
   
   def setup_driver(self):
      optimized_xpaths = self.get_optimized_xpaths()
      
      type_text("\nOptimized XPaths (JSON format):")
      type_text(json.dumps(optimized_xpaths, indent=2))
      
      firefox_options = Options()
      
      # Use your EXACT Firefox profile with proper Selenium method
      import glob
      profiles = glob.glob("/Users/klaus/Library/Application Support/Firefox/Profiles/*.default-release")
      if profiles:
         profile_path = profiles[0]
         type_text("🕒 Opening browser...")
         type_text("")
         type_text(f"    Using Firefox profile: {profile_path}")
         type_text("")
         firefox_options.profile = profile_path  # Use proper Selenium profile assignment
      else:
         # TODO IMPORTANT: Default to random profile or default profile if one is not found
         type_text("WARNING: No Firefox profile found")
         type_text("")
      
      # CRITICAL: Disable webdriver detection
      firefox_options.set_preference("dom.webdriver.enabled", False)
      firefox_options.set_preference("useAutomationExtension", False)
      firefox_options.set_preference("marionette", True)
      
      try:
         service = Service()
         self.driver = webdriver.Firefox(service=service, options=firefox_options)
         self.driver.set_page_load_timeout(30)
         
         # Nuclear option for evasion
         self.driver.execute_script("""
               Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
               delete navigator.__proto__.webdriver;""")
         
      except WebDriverException as e:
         type_text(f"🚫 Error setting up Firefox driver: {e}")
         raise
   
   def get_element_text_from_xpaths(self, element_name, xpaths, default="?", critical=False):
      """Try multiple XPaths until one works"""
      for i, xpath in enumerate(xpaths):
         try:
               time.sleep(0.1)  # Short delay between attempts
               element = self.driver.find_element(By.XPATH, xpath)
               text = element.text.strip()
               if text:  # Only return if we actually got text
                  type_text(f"  {element_name} was found with XPath #{i+1}: {xpath}") # Output successful hit to the console                
                  self._track_xpath_hit(element_name, i, xpath) # Track the successful XPath hit
                  self.save_xpath_statistics() # Update statistics as it goes
                  return text
         except NoSuchElementException:
               continue  # Try next XPath
      
      # If we get here, none of the XPaths worked
      if critical:
         self.critical_element_scrape_fails += 1
         type_text("\n")
         raise Exception(f"CRITICAL: Could not find {element_name} with any XPath from this list: {xpaths}")
      
      # If we get here, nothing was found for a non-critical element
      self.non_critical_element_scrape_fails += 1
      return default
   
   def scrape_job_info(self, url):
      """Scrape job information from a single URL"""
      type_text(f"\nScraping: {url}")
      
      try:
         # Keep the webdriver evasion
         self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
         
         # Navigate to URL
         self.driver.get(url)
         
         # Wait for page to be fully loaded
         WebDriverWait(self.driver, 10).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
         )
         
         time.sleep(1.5) # Give it an extra second
         
         # Define XPATHS for different platforms
         if 'linkedin.com' in url:
            # Arrays of XPaths for each field
               job_title_xpaths = [
                  # Absolute XPaths
                  "/html/body/main/section[1]/div/section[2]/div/div[1]/div/h1",
                  "/html/body/div[5]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[2]/div/h1",
                  "/html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[2]/div/h1",
                  # More flexible XPaths based on the HTML structure
                  "//h1[contains(@class, 'job-details-jobs-unified-top-card__job-title')]",
                  "//h1[contains(@class, 't-24') and contains(@class, 't-bold')]",
                  "//h1[@class='t-24 t-bold inline']",
                  "//div[contains(@class, 'job-details-jobs-unified-top-card__job-title')]//h1",
                  "//h1[contains(text(), 'Engineer') or contains(text(), 'Developer') or contains(text(), 'Manager') or contains(text(), 'Tech') or contains(text(), 'Analyst') or contains(text(), 'Help') or contains(text(), 'Desk') or contains(text(), 'Admin') or contains(text(), 'Network') or contains(text(), 'Desk') or contains(text(), 'Support')]",
                  # Generic h1 elements that are likely to be job titles
                  "//main//h1",
                  "//div[contains(@class, 'main')]//h1",
                  "//h1[not(contains(@class, 'hidden')) and string-length(text()) > 10]",
                  # Fallback to any h1 that's not empty
                  "//h1[normalize-space(text()) != '']"
               ]
               employer_xpaths = [
                  # Absolute XPaths
                  "/html/body/main/section[1]/div/section[2]/div/div[1]/div/h4/div[1]/span[1]/a",
                  "/html/body/div[5]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[1]/div[1]/div/a",
                  "/html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[1]/div[1]/div/a",
                  # Company name in specific container
                  "//div[contains(@class, 'job-details-jobs-unified-top-card__company-name')]//a",
                  "//div[contains(@class, 'job-details-jobs-unified-top-card__company-name')]",
                  # Links with company class patterns
                  "//a[contains(@class, 'DJZxjMmjvRjrlgkfexJvTUxNqCHEnFKxUSdJm')]",
                  
                  # Company links near logos
                  "//div[contains(@class, 'display-flex align-items-center')]//a[contains(@href, '/company/')]",
                  "//a[.//div[contains(@class, 'ivm-image-view-model')]]/following-sibling::div//a",
                  # Text content near company logos
                  "//img[contains(@alt, 'logo')]/ancestor::a/following-sibling::div//a",
                  # Generic company name patterns
                  "//a[not(contains(text(), 'Apply')) and not(contains(text(), 'Save')) and string-length(text()) > 2 and string-length(text()) < 50]"
               ]
               location_xpaths = [
                  # Original absolute XPaths (keep as fallbacks)
                  "/html/body/main/section[1]/div/section[2]/div/div[1]/div/h4/div[1]/span[2]",
                  "/html/body/div[5]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[3]/div/span/span[1]",
                  "/html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[3]/div/span/span[1]",
                  # Location in the tertiary description container
                  "//div[contains(@class, 'job-details-jobs-unified-top-card__tertiary-description-container')]//span[contains(@class, 'tvm__text')][1]",
                  "//div[contains(@class, 'job-details-jobs-unified-top-card__primary-description-container')]//span[contains(@class, 'tvm__text')][1]",
                  # First tvm__text element (usually location)
                  "//span[contains(@class, 'tvm__text') and contains(@class, 'tvm__text--low-emphasis')][1]",
                  # Location patterns in text
                  "//span[contains(@class, 'tvm__text') and (contains(text(), 'United States') or contains(text(), 'FL') or contains(text(), 'MD') or contains(text(), 'PA') or contains(text(), 'VA') or contains(text(), 'DE') or contains(text(), 'CA') or contains(text(), 'NY') or contains(text(), 'TX') or contains(text(), 'Remote') or contains(text(), 'Hybrid'))]",
                  # Before the first separator (·)
                  "//span[contains(@class, 'tvm__text')][preceding-sibling::span[contains(@class, 'white-space-pre')][1]]",
                  # In the location-specific containers
                  "//span[contains(@class, 'tvm__text') and not(contains(text(), 'ago')) and not(contains(text(), 'people')) and not(contains(text(), 'Promoted')) and not(contains(text(), 'Responses'))]",
                  # Generic location fallback
                  "//span[contains(@class, 't-black--light')]//span[1]"
               ]
               pay_rate_xpaths = [
                  # Absolute XPaths
                  "/html/body/div[5]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[4]/button[1]/span/strong",
                  "/html/body/div[5]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[4]/button[1]/span/strong",
                  "/html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[4]/button[1]/span/strong",
                  "/html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[4]/button[1]/span[1]/span/strong",
                  # More flexible XPaths
                  "//strong[contains(., '$')]",
                  "//span[contains(., '$') and (contains(., '/yr') or contains(., '/hr'))]",
                  "//*[contains(text(), '$') and (contains(text(), '/yr') or contains(text(), '/hr'))]",
                  "//button[contains(., '$')]//strong",
                  "//button[contains(., '$')]//span" 
               ]
         elif 'indeed.com' in url:
            # TODO: Indeed XPATHS (these need to be adjusted, both the actual XPaths but also they need to be adjusted to work with the new array input args. for the function 'get_element_text_from_xpaths')
            job_title_xpath = "//h1[@class='jobsearch-JobInfoHeader-title']"
            employer_xpath = "//div[contains(@class, 'jobsearch-InlineCompanyRating')]//a"
            location_xpath = "//div[contains(@class, 'jobsearch-JobInfoHeader-subtitle')]//div[contains(@class, 'location')]"
            pay_rate_xpath = "//span[contains(@class, 'salary')]//span"
         else:
            type_text(f"Unsupported platform for URL: {url}")
            return None
         
         # Scrape information with error handling
         job_info = {
            'Job Title': self.get_element_text_from_xpaths("Job Title", job_title_xpaths, critical=True),
            'Employer': self.get_element_text_from_xpaths("Employer", employer_xpaths, critical=True),
            'Location': self.get_element_text_from_xpaths("Location", location_xpaths),
            'Pay Rate': normalize_pay_rate(self.get_element_text_from_xpaths("Pay Rate", pay_rate_xpaths)), # Normalize pay rate immediately
            'Job Ad': url,
            'Date Found': datetime.now().strftime("%m/%d/%Y")
         }
         
         # Print scraped info for verification
         type_text(f"  Title: {job_info['Job Title']}")
         type_text(f"  Employer: {job_info['Employer']}")
         type_text(f"  Location: {job_info['Location']}")
         type_text(f"  Pay Rate: {job_info['Pay Rate']}")
         
         # Random scrolling after scraping to make it seem less suspicious
         self.human_scroll()
         self.human_delay()
         
         return job_info
         
      except TimeoutException:
         type_text(f"Timeout loading page: {url}")
         return None
      except Exception as e:
         type_text(f"🚫 Error scraping {url}: {e}")
         return None
   
   def linkedin_login(self):
      type_text(f"\n{'='*50}")
      type_text("") # Divider
      type_text("🕒 Navigating to 'https://www.linkedin.com/")
      type_text("")
      
      try:
         target_url = "https://www.linkedin.com/"
         
         # Clear any existing pages
         self.driver.execute_script("window.stop();")
         
         # Navigate to LinkedIn
         self.driver.get(target_url)
         
         # Wait for navigation to complete
         WebDriverWait(self.driver, timeout=10).until(
               lambda d: d.execute_script('return document.readyState') == 'complete'
         )
      except Exception as e:
         type_text(f"🚫 Error navigating to LinkedIn: {e}")
         return False
      
      type_text("🔐 Checking login status...")
      time.sleep(2)
      
      # Check if we're already on the feed page (logged in)
      current_url = self.driver.current_url
      if "linkedin.com/feed" in current_url:
         type_text("✅ Already logged in to LinkedIn (on feed page)")
         return True
      
      # Check if we're on any other LinkedIn page that indicates we're logged in
      if "linkedin.com" in current_url and any(pattern in current_url for pattern in [
         "/feed", "/mynetwork", "/jobs", "/messaging", "/notifications"
      ]):
         type_text("✅ Already logged in to LinkedIn")
         return True
      
      type_text("🔐 Not logged in, proceeding with login...")
      
      # Original login logic
      try:
         """Manual login - just open LinkedIn and wait, also checks for if the user is already logged in"""
         type_text("MANUAL LOGIN REQUIRED:")
         type_text("1. A Firefox window will open")
         type_text("2. Sign in to LinkedIn manually")
         type_text("3. Come back here and press Enter")
         
         self.driver.get("https://www.linkedin.com")
         input("Press Enter AFTER you have successfully signed in...")
         self.signed_in = True
         return True
         
      except TimeoutException:
         type_text("🚫 Login failed or timed out")
         # Check if we might be logged in anyway
         current_url = self.driver.current_url
         if "linkedin.com/feed" in current_url or any(pattern in current_url for pattern in [
               "/feed", "/mynetwork", "/jobs", "/messaging"
         ]):
               type_text("✅ False negative, actually logged in (detected after timeout)")
               return True
         return False
      except Exception as e:
         type_text(f"🚫 Error during login: {e}")
         return False
   
   def print_statistics(self):
      type_text("")
      print_applybot_mascot_w_statistics() # Print the mascot with statistics text
      type_text("")
      self.get_xpath_statistics()
      type_text("")
      self.get_element_scraping_statistics()
   
   def close(self):
      """Close the browser driver"""
      if hasattr(self, 'driver'):
         self.driver.quit()
      self.print_statistics() # Print statistics



# START - Job Listing Pre Processing
def load_config(config_file='config.json'):
   """
      Purpose: Function used to load the config file
      Inputs:
         config_path, string, the file path to the config file
      Output:
         The json contents of the config file from the input.
   """
   if not os.path.exists(config_file):
      type_text(f"⚠️  Config file '{config_file}' not found. Using default settings.")
      return {}
   
   if not os.path.isfile(config_file):
      type_text(f"⚠️  '{config_file}' is not a file. Using default settings.")
      return {}
   
   try:
      with open(config_file, 'r') as f:
         config = json.load(f)
      type_text(f"✅ Config loaded from '{config_file}'")
      return config
   except json.JSONDecodeError as e:
      type_text(f"🚫 Error parsing config file '{config_file}': {e}. Using default settings.")
      return {}
   except Exception as e:
      type_text(f"🚫 Error reading config file '{config_file}': {e}. Using default settings.")
      return {}

def normalize_job_links(links):
   """
   Purpose: Remove all extra fluff from a job listing URL such as tracking stuff, etc.
   Input:
      links, an array strings of job listings urls
   Output:
      normalized_links, an array of normalized string URLs
   """
   normalized_links = []
   number_of_successfully_normalized_links = 0
   
   type_text(f"\n{'='*50}")
   type_text("") # Divider
   type_text("Normalizing Job Listing URLs...")
   
   for link in links:
      # Check if it's a LinkedIn link
      if "linkedin.com" in link:
         # Find the position of "/view/" followed by numbers
         view_index = link.find("/view/")
         if view_index != -1:
               # Find the next slash after "/view/######"
               start_search = view_index + 6  # Move past "/view/"
               # Look for the next slash after the job ID numbers
               next_slash = link.find("/", start_search)
               if next_slash != -1:
                  # Keep everything up to and including the slash after the job ID
                  normalized_link = link[:next_slash + 1]
                  number_of_successfully_normalized_links += 1
                  normalized_links.append(normalized_link)
               else:
                  # If no trailing slash found, use the original link
                  number_of_successfully_normalized_links += 1
                  normalized_links.append(link)
         else:
               # If no "/view/" pattern found, use original link
               normalized_links.append(link)
               
      # Check if it's an Indeed link
      elif "indeed.com" in link:
         # Find the position of "/viewjob?jk="
         jk_index = link.find("/viewjob?jk=")
         if jk_index != -1:
            # Find the next slash after the job key
            start_search = jk_index + 12  # Move past "/viewjob?jk="
            # Look for the next slash or question mark or end of string
            next_slash = link.find("/", start_search)
            next_question = link.find("?", start_search)
            next_ampersand = link.find("&", start_search)
            
            # Find the earliest special character after the job key
            end_positions = [pos for pos in [next_slash, next_question, next_ampersand] if pos != -1]
            if end_positions:
               end_pos = min(end_positions)
               normalized_link = link[:end_pos]
               number_of_successfully_normalized_links += 1
               normalized_links.append(normalized_link)
            else:
               # If no special characters found, use the entire link
               number_of_successfully_normalized_links += 1
               normalized_links.append(link)
         else:
            # If no "/viewjob?jk=" pattern found, use original link
            normalized_links.append(link)
      
      # If it's neither LinkedIn nor Indeed
      else:
         type_text(f"Invalid link (not LinkedIn or Indeed): {link}")
   
   type_text(f"Successfully normalized {number_of_successfully_normalized_links}/{len(links)} of input links.")
   return normalized_links

def read_job_links(csv_file_path):
   """
      Purpose: Read job links from CSV file
      Input:
         csv_file_path, the string file path to the CSV file containing the job listing URLs
      Output:
         An array of job listing URLs
   """
   job_links = []
   try:
      with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
         reader = csv.reader(file)
         for row in reader:
               if row and row[0].strip():
                  job_links.append(row[0].strip())
      return job_links
   except Exception as e:
      type_text(f"🚫 Error reading CSV file: {e}")
      return []

def remove_duplicate_links(links):
   """
      Purpose: Remove duplicate links while preserving order
      Input:
         links, an array strings of job listings urls
      Output:
         unique_links, an array of unique links
   """
   seen = set()
   unique_links = []
   for link in links:
      if link not in seen:
         seen.add(link)
         unique_links.append(link)
   return unique_links

def pre_process_job_links(csv_file_path, ascending_alphabetically=True):
   """
      Purpose: Sorts the links in the CSV file input by their domain alphabetically, removes duplicates and normalizes links. This is so that the job scraper can handle different platforms such as LinkedIn and Indeed separately
      Input:
         csv_file_path, the string file path to the CSV file containing the job listing URLs
         ascending_alphabetically, boolean used to dictate if it should be sorted A-Z (default, True), or Z-A (False)
      Output:
         cleaned_links, An array of job listing URLs (string) sorted alphabetically, rid of duplicates and whose links are normalized
   """
   try:
      # Read job links from CSV file
      job_links = read_job_links(csv_file_path)
      
      # Remove duplicates while preserving order initially
      unique_links = remove_duplicate_links(job_links)
      normalized_job_links = normalize_job_links(unique_links)
      
      # Extract domain from each URL and create tuples of (domain, url)
      domain_url_pairs = []
      for url in normalized_job_links:
         try:
            # Parse the URL to extract the domain
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            # Remove 'www.' prefix if present for consistent sorting
            if domain.startswith('www.'):
               domain = domain[4:]
            domain_url_pairs.append((domain, url))
         except Exception:
            # If URL parsing fails, use the original URL as domain
            domain_url_pairs.append(('', url))
      
      # Sort by domain
      sorted_pairs = sorted(domain_url_pairs, key=lambda x: x[0], reverse=not ascending_alphabetically)
      
      # Extract just the URLs in sorted order
      cleaned_links = [url for domain, url in sorted_pairs]
      
      return cleaned_links
      
   except Exception as e:
      type_text(f"🚫 Error sorting job links by domain: {e}")
      return []
# STOP - Job Listing Pre Processing


# START - Job Listing Post Processing
# TODO: find_location_state() | returns the shortened state name. E.x.: West Chester, PA --> PA, stuff like that

def normalize_pay_rate(pay_rate_text):
   """
   Purpose: Normalize salary input to per annum format.
   Inputs:
      pay_rate_text, string, a string containing the column contents of the 'Pay Rate' column from the output of the ApplyBot.
   Output:
      Returns normalized salary string or "?" for unknown values.
   """
   
   # If there was no pay rate and the scraper grabbed the wrong information
   if "hybrid" in pay_rate_text.lower() or "on-site" in pay_rate_text.lower() or "site" in pay_rate_text.lower() or "remote" in pay_rate_text.lower():
      return "?"
   
   if pay_rate_text == "?" or not pay_rate_text or pd.isna(pay_rate_text):
      return "?"
   
   # Convert to string and lowercase for consistent processing
   text = str(pay_rate_text).lower().strip()
   
   # Handle the specific case of "$30/yr" typo (likely meant $30/hr)
   if re.search(r'\$\s*\d+\.?\d*/yr', text) and not re.search(r'k/yr', text):
      # Extract the numeric value and assume it was meant to be per hour
      match = re.search(r'\$\s*(\d+\.?\d*)/yr', text)
      if match:
         hourly_rate = float(match.group(1))
         # Only convert if it's an unreasonably low annual salary (likely typo)
         if hourly_rate < 100:  # Assuming annual salaries under $100 are typos
               annual_salary = hourly_rate * 40 * 52  # 40 hrs/week * 52 weeks
               return f"${annual_salary:,.0f}"
   
   # Handle hourly rates (single or range)
   hourly_matches = re.findall(r'\$\s*(\d+\.?\d*)\s*/hr', text)
   if hourly_matches:
      if len(hourly_matches) == 1:
         # Single hourly rate
         hourly_rate = float(hourly_matches[0])
         annual_salary = hourly_rate * 40 * 52
         return f"${annual_salary:,.0f}"
      elif len(hourly_matches) == 2:
         # Hourly range
         hourly_low = float(hourly_matches[0])
         hourly_high = float(hourly_matches[1])
         annual_low = hourly_low * 40 * 52
         annual_high = hourly_high * 40 * 52
         midpoint = (annual_low + annual_high) / 2
         midpoint_rounded = (midpoint // 1000) * 1000  # Round down to nearest thousand
         note = f"Original range: ${annual_low:,.0f}/yr - ${annual_high:,.0f}/yr"
         return f"${midpoint_rounded:,.0f}", note
   
   # Handle annual salaries with K notation
   k_match = re.search(r'\$\s*(\d+\.?\d*)\s*k\s*/yr', text)
   if k_match:
      annual_salary = float(k_match.group(1)) * 1000
      return f"${annual_salary:,.0f}"
   
   # Handle explicit annual salaries
   annual_match = re.search(r'\$\s*(\d{3,})\s*/yr', text)
   if annual_match:
      annual_salary = int(annual_match.group(1))
      return f"${annual_salary:,.0f}"
   
   # Handle annual ranges
   annual_range_match = re.findall(r'\$\s*(\d{3,}(?:,\d{3})*)\s*/yr', text)
   if annual_range_match and len(annual_range_match) == 2:
      annual_low = int(annual_range_match[0].replace(',', ''))
      annual_high = int(annual_range_match[1].replace(',', ''))
      midpoint = (annual_low + annual_high) / 2
      midpoint_rounded = (midpoint // 1000) * 1000  # Round down to nearest thousand
      note = f"Original range: ${annual_low:,.0f}/yr - ${annual_high:,.0f}/yr"
      return f"${midpoint_rounded:,.0f}", note
   
   # Handle "up to" hourly rates
   upto_match = re.search(r'up to \$\s*(\d+\.?\d*)\s*/hr', text)
   if upto_match:
      hourly_rate = float(upto_match.group(1))
      annual_salary = hourly_rate * 40 * 52
      return f"${annual_salary:,.0f}"
   
   # Handle "starting at" formats
   starting_match = re.search(r'starting at \$\s*(\d+\.?\d*)\s*k\s*/yr', text)
   if starting_match:
      annual_salary = float(starting_match.group(1)) * 1000
      return f"${annual_salary:,.0f}"
   
   # If no patterns match but it's not "?", return original
   if text != "?":
      return pay_rate_text
   
   return "?"

def normalize_pay_rate_csv(csv_file_path):
   """
   Purpose: Read CSV file, normalize 'Pay Rate' column entries, and overwrite the file. Print statistics about the normalization process.
   Inputs:
      csv_file_path, string, file path to the csv that contains the output of the ApplyBot job scraping process
   Output:
      Prints to the console the statistics for the normalization process.
      Adjusts the CSV file inplace to normalize the pay rate.
   """
   try:
      # Read the CSV file
      df = pd.read_csv(csv_file_path)
      
      # Check if 'Pay Rate' column exists
      if 'Pay Rate' not in df.columns:
         type_text(f"🚫 Error: 'Pay Rate' column not found in {csv_file_path}")
         return
      
      # Initialize counters
      fixed_count = 0
      unchanged_count = 0
      question_mark_count = 0
      unparseable_count = 0
      
      # Process each entry in the 'Pay Rate' column
      normalized_rates = []
      notes_list = []
      for original_rate in df['Pay Rate']:
         normalized, note = normalize_pay_rate(original_rate)
         normalized_rates.append(normalized)
         notes_list.append(note)
         
         # Count statistics
         if original_rate == "?" or not original_rate or pd.isna(original_rate):
               question_mark_count += 1
         elif normalized != original_rate:
               fixed_count += 1
         elif normalized == original_rate and normalized != "?":
               unparseable_count += 1
         else:
               unchanged_count += 1
      
      # Update the DataFrame with normalized rates and notes
      df['Pay Rate'] = normalized_rates
      # Add notes to existing 'Notes' column or create new one
      if 'Notes' in df.columns:
         # Combine existing notes with new range notes
         for i, note in enumerate(notes_list):
               if note:  # If there's a new note
                  if pd.isna(df.at[i, 'Notes']) or df.at[i, 'Notes'] == "":
                     df.at[i, 'Notes'] = note
                  else:
                     df.at[i, 'Notes'] = f"{df.at[i, 'Notes']}; {note}"
      else:
         df['Notes'] = notes_list
      
      # Overwrite the original CSV file
      df.to_csv(csv_file_path, index=False)
      
      # Print statistics
      type_text(f"Normalization completed for: {csv_file_path}")
      type_text(f"Entries fixed: {fixed_count}")
      type_text(f"Entries that could not be parsed: {unparseable_count}")
      type_text(f"Entries that were '?': {question_mark_count}")
      type_text(f"Total entries processed: {len(df)}")
      
   except FileNotFoundError:
      type_text(f"🚫 Error: File {csv_file_path} not found")
   except Exception as e:
      type_text(f"🚫 Error processing file: {e}")
# STOP - Job Listing Post Processing

# START - Print functions
def print_applybot_mascot_w_statistics():
   type_text("    ∧___∧        __ _        _   _     _   _          ")
   type_text("   ( •ㅅ•)      / _\ |_ __ _| |_(_)___| |_(_) ___ ___ ")
   type_text("   /     ♡      \ \| __/ _` | __| / __| __| |/ __/ __|")
   type_text("   (   ⌒ ヽ     _\ \ || (_| | |_| \__ \ |_| | (__\__ \\")
   type_text("   ＼_ﾉ  ＿」   \__/\__\__,_|\__|_|___/\__|_|\___|___/")
   type_text("    ♪ ~ ♪")

def print_applybot_mascot():
   type_text("    ∧___∧")
   type_text("   ( •ㅅ•) ")
   type_text("   /     ♡ ")
   type_text("   (   ⌒ ヽ  ")
   type_text("   ＼_ﾉ  ＿」  ")
   type_text("    ♪ ~ ♪")

def print_applybot_intro():
   type_text("")
   type_text("╭─────────────────╮")
   type_text("│    ApplyBot     │")
   type_text("╰─────────────────╯")
   type_text("")
   print_applybot_mascot() # Mascot!
   type_text("")
   type_text("   Made by cZAlpha")
   type_text("")

def type_text(text, delay=0.004):
   """Print text with typing effect"""
   for char in text:
      print(char, end='', flush=True)  # ✅ CORRECT - use print()
      time.sleep(delay)
   print()  # New line at the end
# STOP - Print functions



def main():
   parser = argparse.ArgumentParser(description='Scrape job information from links')
   input_csv = parser.add_argument('input_csv', help='Input CSV file with job links')
   parser.add_argument('output_csv', help='Output CSV file for job information')
   parser.add_argument('--config', default='config.json', help='Config file path')
   parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
   
   args = parser.parse_args()
   
   type_text(f"\n{'='*50}")
   type_text("") # Divider
   print_applybot_intro()
   
   # Validate input CSV exists
   if not os.path.exists(args.input_csv): # No input csv file found
      type_text(f"\n{'='*50}")
      type_text("") # Divider
      type_text(f"🚫 Input CSV file '{args.input_csv}' not found!")
      type_text("     In the future, you will not need an input file, as ApplyBot will find jobs for you, but for now, you must source URLs yourself. Place these URLs into a CSV file where each new line contains one link, preferrably with an HTTPS:// in front.")
      return
   else: # Input file was successfully found
      cleaned_links = pre_process_job_links(args.input_csv) # Sort all job links by domain, remove duplicates and normalize links
   
   # Fetch config file contents
   type_text(f"\n{'='*50}")
   type_text("") # Divider
   config = load_config(args.config)
   
   type_text(f"\n{'='*50}") # Divider
   
   # Read and remove duplicate links
   type_text(f"\n🕒 Parsing job links from {args.input_csv}...\n\n")
   if (len(cleaned_links) <= 0): # Error check
      type_text(f"🚫 Did not find any job links in {args.input_csv}! Check your input CSV file path, the file contents, and try again.")
      return
   type_text(f"✅ Found {len(cleaned_links)} unique job links")
   type_text(f"\n{'='*50}")
   type_text("") # Divider
   
   # Initialize scraper (will call setup_driver, which will open browser)
   scraper = JobScraper(config=config, headless=args.headless)
   
   # Login manually if needed
   scraper.linkedin_login()
   
   # Prepare output CSV
   fieldnames = ['Job Title', 'Employer', 'Location', 'Pay Rate', 'Job Ad', 'Date Found']
   
   try:
      with open(args.output_csv, 'w', newline='', encoding='utf-8') as csvfile:
         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
         writer.writeheader()
         
         successful_scrapes = 0
         failed_links = []
         
         for i, link in enumerate(cleaned_links, 1):
            type_text(f"\n{'='*50}") # Divider
            type_text(f"\nProcessing link {i}/{len(cleaned_links)}")
            
            # Scrape the job info
            job_info = scraper.scrape_job_info(link)
            
            if job_info:
               writer.writerow(job_info)
               csvfile.flush()  # Ensure data is written immediately
               successful_scrapes += 1
               type_text(f"✓ Successfully scraped and saved")
            else:
               failed_links.append(link)
               type_text(f"✗ Failed to scrape")
               
               # Pause on failure for user input
               type_text("Press Enter to continue to next job, or Ctrl+C to exit...")
               try:
                  input()
               except KeyboardInterrupt:
                  type_text("\nUser interrupted. Saving progress...")
                  break
            
            # Random delay between requests to avoid being blocked
            time.sleep(random.uniform(2, 4))
      
      # Summary after scraping is done 
      type_text(f"\n{'='*50}") # Divider
      type_text(f"Scraping Complete!")
      type_text(f"Successful: {successful_scrapes}")
      type_text(f"Failed: {len(failed_links)}")
      type_text(f"Output saved to: {args.output_csv}")
      
      # Show any links that failed to be scraped
      if failed_links:
         type_text(f"\nFailed links:")
         for link in failed_links:
               type_text(f"  - {link}")
      
      # Post Processing
      type_text(f"\n{'='*50}") # Divider
   
   except Exception as e:
      type_text(f"\n{'='*50}") # Divider
      type_text(f"Unexpected error: {e}")
      type_text("Press Enter to exit...")
      input()
   finally:
      scraper.close()



if __name__ == "__main__":
   main()