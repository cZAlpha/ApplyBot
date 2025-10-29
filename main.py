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
         print(f"Mouse movement failed: {e}")
   
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
   
   def setup_driver(self):
      firefox_options = Options()
      
      # Use your EXACT Firefox profile with proper Selenium method
      import glob
      profiles = glob.glob("/Users/klaus/Library/Application Support/Firefox/Profiles/*.default-release")
      if profiles:
         profile_path = profiles[0]
         print("🕒 Opening browser...", "\n")
         print(f"    Using Firefox profile: {profile_path}", "\n")
         firefox_options.profile = profile_path  # Use proper Selenium profile assignment
      else:
         # TODO IMPORTANT: Default to random profile or default profile if one is not found
         print("WARNING: No Firefox profile found", "\n")
      
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
         print(f"🚫 Error setting up Firefox driver: {e}")
         raise
   
   def get_element_text_from_xpaths(self, element_name, xpaths, default="?", critical=False):
      """Try multiple XPaths until one works"""
      for i, xpath in enumerate(xpaths):
         try:
               time.sleep(0.1)  # Short delay between attempts
               element = self.driver.find_element(By.XPATH, xpath)
               text = element.text.strip()
               if text:  # Only return if we actually got text
                  print(f"  {element_name} was found with XPath #{i+1}: {xpath}")
                  return text
         except NoSuchElementException:
               continue  # Try next XPath
      
      # If we get here, none of the XPaths worked
      if critical:
         self.critical_element_scrape_fails += 1
         print("\n")
         raise Exception(f"CRITICAL: Could not find {element_name} with any XPath from this list: {xpaths}")
      
      # If we get here, nothing was found for a non-critical element
      self.non_critical_element_scrape_fails += 1
      return default
   
   def scrape_job_info(self, url):
      """Scrape job information from a single URL"""
      print(f"\nScraping: {url}")
      
      try:
         # Keep the webdriver evasion
         self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
         
         # Navigate to URL
         self.driver.get(url)
         
         # Wait for page to be fully loaded
         WebDriverWait(self.driver, 10).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
         )
         
         time.sleep(1) # Give it an extra second
         
         # Define XPATHS for different platforms
         if 'linkedin.com' in url:
            # Arrays of XPaths for each field
               job_title_xpaths = [
                  "/html/body/main/section[1]/div/section[2]/div/div[1]/div/h1",
                  "/html/body/div[5]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[2]/div/h1",
                  "/html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[2]/div/h1",
                  "/html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[2]/div/h1"
               ]
               employer_xpaths = [
                  "/html/body/main/section[1]/div/section[2]/div/div[1]/div/h4/div[1]/span[1]/a",
                  "/html/body/div[5]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[1]/div[1]/div/a",
                  "/html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[1]/div[1]/div/a"
               ]
               location_xpaths = [
                  "/html/body/main/section[1]/div/section[2]/div/div[1]/div/h4/div[1]/span[2]",
                  "/html/body/div[5]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[3]/div/span/span[1]",
                  "/html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[3]/div/span/span[1]"
               ]
               pay_rate_xpaths = [
                  "/html/body/div[5]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[4]/button[1]/span/strong",
                  "/html/body/div[5]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[4]/button[1]/span/strong",
                  "/html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[4]/button[1]/span/strong",
                  "/html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[4]/button[1]/span[1]/span/strong"
               ]
         elif 'indeed.com' in url:
            # TODO: Indeed XPATHS (these need to be adjusted, both the actual XPaths but also they need to be adjusted to work with the new array input args. for the function 'get_element_text_from_xpaths')
            job_title_xpath = "//h1[@class='jobsearch-JobInfoHeader-title']"
            employer_xpath = "//div[contains(@class, 'jobsearch-InlineCompanyRating')]//a"
            location_xpath = "//div[contains(@class, 'jobsearch-JobInfoHeader-subtitle')]//div[contains(@class, 'location')]"
            pay_rate_xpath = "//span[contains(@class, 'salary')]//span"
         else:
            print(f"Unsupported platform for URL: {url}")
            return None
         
         # Scrape information with error handling
         job_info = {
            'Job Title': self.get_element_text_from_xpaths("Job Title", job_title_xpaths, critical=True),
            'Employer': self.get_element_text_from_xpaths("Employer", employer_xpaths, critical=True),
            'Location': self.get_element_text_from_xpaths("Location", location_xpaths),
            'Pay Rate': self.get_element_text_from_xpaths("Pay Rate", pay_rate_xpaths),
            'Job Ad': url,
            'Date Found': datetime.now().strftime("%m/%d/%Y")
         }
         
         # Print scraped info for verification
         print(f"  Title: {job_info['Job Title']}")
         print(f"  Employer: {job_info['Employer']}")
         print(f"  Location: {job_info['Location']}")
         print(f"  Pay Rate: {job_info['Pay Rate']}")
         
         # Random scrolling after scraping to make it seem less suspicious
         self.human_scroll()
         self.human_delay()
         
         return job_info
         
      except TimeoutException:
         print(f"Timeout loading page: {url}")
         return None
      except Exception as e:
         print(f"🚫 Error scraping {url}: {e}")
         return None
   
   def linkedin_login(self):
      print(f"\n{'='*50}", "\n") # Divider
      print("🕒 Navigating to 'https://www.linkedin.com/", "\n")
      
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
         print(f"🚫 Error navigating to LinkedIn: {e}")
         return False
      
      print("🔐 Checking login status...")
      time.sleep(2)
      
      # Check if we're already on the feed page (logged in)
      current_url = self.driver.current_url
      if "linkedin.com/feed" in current_url:
         print("✅ Already logged in to LinkedIn (on feed page)")
         return True
      
      # Check if we're on any other LinkedIn page that indicates we're logged in
      if "linkedin.com" in current_url and any(pattern in current_url for pattern in [
         "/feed", "/mynetwork", "/jobs", "/messaging", "/notifications"
      ]):
         print("✅ Already logged in to LinkedIn")
         return True
      
      print("🔐 Not logged in, proceeding with login...")
      
      # Original login logic
      try:
         """Manual login - just open LinkedIn and wait, also checks for if the user is already logged in"""
         print("MANUAL LOGIN REQUIRED:")
         print("1. A Firefox window will open")
         print("2. Sign in to LinkedIn manually")
         print("3. Come back here and press Enter")
         
         self.driver.get("https://www.linkedin.com")
         input("Press Enter AFTER you have successfully signed in...")
         self.signed_in = True
         return True
         
      except TimeoutException:
         print("🚫 Login failed or timed out")
         # Check if we might be logged in anyway
         current_url = self.driver.current_url
         if "linkedin.com/feed" in current_url or any(pattern in current_url for pattern in [
               "/feed", "/mynetwork", "/jobs", "/messaging"
         ]):
               print("✅ False negative, actually logged in (detected after timeout)")
               return True
         return False
      except Exception as e:
         print(f"🚫 Error during login: {e}")
         return False
   
   def close(self):
      """Close the browser driver"""
      if hasattr(self, 'driver'):
         self.driver.quit()



# START - Job Listing Preparation
def load_config(config_file='config.json'):
   """
      Purpose: Function used to load the config file
      Inputs:
         config_path, string, the file path to the config file
      Output:
         The json contents of the config file from the input.
   """
   if not os.path.exists(config_file):
      print(f"⚠️  Config file '{config_file}' not found. Using default settings.")
      return {}
   
   if not os.path.isfile(config_file):
      print(f"⚠️  '{config_file}' is not a file. Using default settings.")
      return {}
   
   try:
      with open(config_file, 'r') as f:
         config = json.load(f)
      print(f"✅ Config loaded from '{config_file}'")
      return config
   except json.JSONDecodeError as e:
      print(f"🚫 Error parsing config file '{config_file}': {e}. Using default settings.")
      return {}
   except Exception as e:
      print(f"🚫 Error reading config file '{config_file}': {e}. Using default settings.")
      return {}

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
      print(f"🚫 Error reading CSV file: {e}")
      return []

def remove_duplicate_links(links):
   """
      Purpose: Remove duplicate links while preserving order
      Input:
         links, an array of links
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

def sort_job_links_by_domain(csv_file_path, ascending_alphabetically=True):
   """
      Purpose: Sorts the links in the CSV file input by their domain alphabetically. This is so that the job scraper can handle different platforms such as LinkedIn and Indeed separately
      Input:
         csv_file_path, the string file path to the CSV file containing the job listing URLs
         ascending_alphabetically, boolean used to dictate if it should be sorted A-Z (default, True), or Z-A (False)
      Output:
         An array of job listing URLs sorted alphabetically
   """
   try:
      # Read job links from CSV file
      job_links = read_job_links(csv_file_path)
      
      # Remove duplicates while preserving order initially
      unique_links = remove_duplicate_links(job_links)
      
      # Extract domain from each URL and create tuples of (domain, url)
      domain_url_pairs = []
      for url in unique_links:
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
      sorted_links = [url for domain, url in sorted_pairs]
      
      return sorted_links
      
   except Exception as e:
      print(f"🚫 Error sorting job links by domain: {e}")
      return []
# STOP - Job Listing Preparation


# START - Post Processing
def normalize_pay_rate(pay_rate_text):
   """
   Purpose: Normalize salary input to per annum format.
   Inputs:
      pay_rate_text, string, a string containing the column contents of the 'Pay Rate' column from the output of the ApplyBot.
   Output:
      Returns normalized salary string or "?" for unknown values.
   """
   if pay_rate_text == "?" or not pay_rate_text or pd.isna(pay_rate_text):
      return "?", ""
   
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
               return f"${annual_salary:,.0f}", ""
   
   # Handle hourly rates (single or range)
   hourly_matches = re.findall(r'\$\s*(\d+\.?\d*)\s*/hr', text)
   if hourly_matches:
      if len(hourly_matches) == 1:
         # Single hourly rate
         hourly_rate = float(hourly_matches[0])
         annual_salary = hourly_rate * 40 * 52
         return f"${annual_salary:,.0f}", ""
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
      return f"${annual_salary:,.0f}", ""
   
   # Handle explicit annual salaries
   annual_match = re.search(r'\$\s*(\d{3,})\s*/yr', text)
   if annual_match:
      annual_salary = int(annual_match.group(1))
      return f"${annual_salary:,.0f}", ""
   
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
      return f"${annual_salary:,.0f}", ""
   
   # Handle "starting at" formats
   starting_match = re.search(r'starting at \$\s*(\d+\.?\d*)\s*k\s*/yr', text)
   if starting_match:
      annual_salary = float(starting_match.group(1)) * 1000
      return f"${annual_salary:,.0f}", ""
   
   # If no patterns match but it's not "?", return original
   if text != "?":
      return pay_rate_text, ""
   
   return "?", ""

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
         print(f"🚫 Error: 'Pay Rate' column not found in {csv_file_path}")
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
      print(f"Normalization completed for: {csv_file_path}")
      print(f"Entries fixed: {fixed_count}")
      print(f"Entries that could not be parsed: {unparseable_count}")
      print(f"Entries that were '?': {question_mark_count}")
      print(f"Total entries processed: {len(df)}")
      
   except FileNotFoundError:
      print(f"🚫 Error: File {csv_file_path} not found")
   except Exception as e:
      print(f"🚫 Error processing file: {e}")
# STOP - Post Processing


def main():
   parser = argparse.ArgumentParser(description='Scrape job information from links')
   input_csv = parser.add_argument('input_csv', help='Input CSV file with job links')
   parser.add_argument('output_csv', help='Output CSV file for job information')
   parser.add_argument('--config', default='config.json', help='Config file path')
   parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
   
   args = parser.parse_args()
   
   # Validate input CSV exists
   if not os.path.exists(args.input_csv):
      print(f"\n{'='*50}", "\n") # Divider
      print(f"🚫 Input CSV file '{args.input_csv}' not found!")
      print("     In the future, you will not need an input file, as ApplyBot will find jobs for you, but for now, you must source URLs yourself. Place these URLs into a CSV file where each new line contains one link, preferrably with an HTTPS:// in front.")
      return
   
   # Fetch config file contents
   print(f"\n{'='*50}", "\n") # Divider
   config = load_config(args.config)
   
   print(f"\n{'='*50}") # Divider
   
   # Read and remove duplicate links
   print(f"\n🕒 Parsing job links from {args.input_csv}...\n\n")
   links = read_job_links(args.input_csv)
   unique_links = remove_duplicate_links(links)
   if (len(unique_links) <= 0): # Error check
      print(f"🚫 Did not find any job links in {args.input_csv}! Check your input CSV file path, the file contents, and try again.")
      return
   print(f"✅ Found {len(unique_links)} unique job links")
   print(f"\n{'='*50}", "\n") # Divider
   
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
         
         for i, link in enumerate(unique_links, 1):
            print(f"\n{'='*50}") # Divider
            print(f"\nProcessing link {i}/{len(unique_links)}")
            
            # Scrape the job info
            job_info = scraper.scrape_job_info(link)
            
            if job_info:
               writer.writerow(job_info)
               csvfile.flush()  # Ensure data is written immediately
               successful_scrapes += 1
               print(f"✓ Successfully scraped and saved")
            else:
               failed_links.append(link)
               print(f"✗ Failed to scrape")
               
               # Pause on failure for user input
               print("Press Enter to continue to next job, or Ctrl+C to exit...")
               try:
                  input()
               except KeyboardInterrupt:
                  print("\nUser interrupted. Saving progress...")
                  break
            
            # Random delay between requests to avoid being blocked
            time.sleep(random.uniform(2, 4))
      
      # Summary after scraping is done 
      print(f"\n{'='*50}") # Divider
      print(f"Scraping Complete!")
      print(f"Successful: {successful_scrapes}")
      print(f"Failed: {len(failed_links)}")
      print(f"Output saved to: {args.output_csv}")
      
      # Show any links that failed to be scraped
      if failed_links:
         print(f"\nFailed links:")
         for link in failed_links:
               print(f"  - {link}")
      
      # Post Processing
      print(f"\n{'='*50}") # Divider
      normalize_pay_rate_csv(args.output_csv)
   
   except Exception as e:
      print(f"\n{'='*50}") # Divider
      print(f"Unexpected error: {e}")
      print("Press Enter to exit...")
      input()
   finally:
      scraper.close()



if __name__ == "__main__":
   main()