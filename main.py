import os
import re
import sys
import csv
import time
import math
import time
import json
import glob
import random
import argparse
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException



class ApplyBot:
   def __init__(self, config=None, headless=False):
      if config == None: # No config, throw error
         type_text("ERROR: No config was passed into ApplyBot. Please check that you have a configuration file and gave it as an argument when calling main.py!")
         return
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
      self.jobs_thrown_out_for_lack_of_security_clearance = 0 # The number of jobs thrown out due to the user not meeting the job's security clearance requirements
   
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
   
   def setup_driver(self):
      optimized_xpaths = self.get_optimized_xpaths()
      
      # Check for if the xpath json file exists, only output to console if it does
      if os.path.exists("xpath_stats.json"):
         type_text("Optimized Job Scraping XPaths (JSON format)")
         # Optional printing of the optimized paths to the console
         # type_text(json.dumps(optimized_xpaths, indent=2))
         type_text("")
      
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
   def _track_xpath_hit(self, element_name, xpath_string):
      """Track which XPaths are successful for which elements | Statistical tracking function"""
      # Load current statistics from file
      stats = self._load_xpath_stats_from_file()
      
      if element_name not in stats:
         stats[element_name] = {}
      
      # Use the actual XPath string as the key (GOOD FORMAT)
      if xpath_string not in stats[element_name]:
         stats[element_name][xpath_string] = {
               'count': 0
         }
      
      stats[element_name][xpath_string]['count'] += 1
      
      # Save updated statistics back to file
      self._save_xpath_stats_to_file(stats)
   
   def get_optimized_xpaths(self):
      """Get optimized XPath lists based on hit statistics"""
      stats = self._load_xpath_stats_from_file()
      optimized = {}
      
      for element_name, xpaths in stats.items():
         # Sort by hit count descending
         sorted_xpaths = sorted(xpaths.items(), key=lambda x: x[1]['count'], reverse=True)
         
         # Create optimized list - just the XPath strings in order of most successful
         optimized[element_name] = [xpath_string for xpath_string, data in sorted_xpaths]
      
      return optimized
   
   def get_xpath_statistics(self):
      """Print out XPath hit statistics"""
      stats = self._load_xpath_stats_from_file()
      
      type_text("XPATH HIT STATISTICS")
      
      for element_name, xpaths in stats.items():
         type_text(f"\n{element_name}:")
         
         # Sort by count descending
         sorted_xpaths = sorted(xpaths.items(), key=lambda x: x[1]['count'], reverse=True)
         
         for xpath_string, data in sorted_xpaths:
               type_text(f"  {data['count']} hits: {xpath_string}")
   
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
   
   def get_security_clearance_statistics(self):
      type_text("SECURITY CLEARANCE STATISTICS")
      type_text("")
      if (self.jobs_thrown_out_for_lack_of_security_clearance <= 0): # If no jobs were thrown out due to lack of security clearance
         type_text("No jobs removed due to lack of a security clearance / too low of a security clearance.")
      else: 
         type_text("Number of jobs thrown out due to lack of clearance: " + str(self.jobs_thrown_out_for_lack_of_security_clearance))
   # STOP - Statistics
   
   def get_element_text_from_xpaths(self, element_name, xpaths, default="?", critical=False):
      """Try multiple XPaths until one works"""
      for i, xpath in enumerate(xpaths):
         try:
               time.sleep(0.1)  # Short delay between attempts
               element = self.driver.find_element(By.XPATH, xpath)
               text = element.text.strip()
               if text:  # Only return if we actually got text
                  type_text(f"  {element_name} was found with XPath #{i+1}: {xpath}") # Output successful hit to the console                
                  self._track_xpath_hit(element_name, xpath) # Track the successful XPath hit
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
         
         # Scrape the job listing information
         job_title = self.get_element_text_from_xpaths("Job Title", job_title_xpaths, critical=True)
         employer = self.get_element_text_from_xpaths("Employer", employer_xpaths, critical=True)
         location = self.get_element_text_from_xpaths("Location", location_xpaths)
         normalized_pay_rate = normalize_pay_rate(self.get_element_text_from_xpaths("Pay Rate", pay_rate_xpaths)) # Normalize pay rate immediately
         pay_rate = normalized_pay_rate[0] # Grab first element of the tuple, that being the pay rate
         pay_rate_notes = normalized_pay_rate[1] # Grab the second element of the tuple, that being the notes
         security_clearance = self.detect_security_clearance() # Detected security clearance
         is_user_cleared =  self.compare_clearance_from_config(security_clearance) # Compares the user's security clearance against the detected security clearance
         
         # If the user is not cleared for the job's security clearance requirements, disregard job posting
         if not is_user_cleared: 
            self.jobs_thrown_out_for_lack_of_security_clearance += 1
            type_text(f"🚫 Job Thrown Out Due to Lack of Security Clearance!")
            return "incompatible"
         
         # Structure the scraped information 
         job_info = {
            'Job Title': job_title,
            'Employer': employer,
            'Location': location,
            'Pay Rate': pay_rate, 
            'Job Ad': url,
            'Date Found': datetime.now().strftime("%m/%d/%Y"),
            'Notes': pay_rate_notes, # Any other notes can be appended to this as needed
            'Security Clearance': security_clearance # If the user does not possess a security clearance, this will always be 'none', as jobs requiring that will be thrown out
         }
         
         # Print scraped info for verification
         type_text(f"  Title: {job_info['Job Title']}")
         type_text(f"  Employer: {job_info['Employer']}")
         type_text(f"  Location: {job_info['Location']}")
         type_text(f"  Pay Rate: {job_info['Pay Rate']}")
         type_text(f"  Notes: {job_info['Notes']}")
         type_text(f"  Clearance Level: {job_info['Security Clearance']}")
         
         # Random scrolling after scraping to make it seem less suspicious
         self.human_scroll()
         self.human_delay()
         
         return job_info
         
      except TimeoutException:
         type_text(f"🕒 Timeout loading page: {url}")
         return None
      except Exception as e:
         type_text(f"🚫 Error scraping {url}: {e}")
         return None
   
   def fill_in_application_information(self, url):
      """
         Purpose: Function that handles filling in job application information based on what domain from the input args 'url' is passed in
         Inputs:
            url: The url of the job application
         Output:
            True if successful, false otherwise
      """
      # Check for config existence and None errors
      if self.config is None:
         type_text("🚫 ERROR | fill_in_application_information | Config not found! ")
         return False
      if 'greenhouse.io' in url:         
         # Navigate to URL
         self.driver.get(url)
         
         # Wait for page to be fully loaded
         WebDriverWait(self.driver, 10).until(
               lambda driver: driver.execute_script("return document.readyState") == "complete"
         )
         
         time.sleep(1.5) # Give it an extra second
         
         type_text("fill_in_application_information | greenhouse.io | filling in application information...")
         
         try:
            # Fill basic information fields
            self._fill_basic_information_greenhouse_io(self.config)
            type_text("fill_in_application_information | _fill_basic_information_greenhouse_io | ok")
            
            # Fill phone information
            self._fill_phone_information_greenhouse_io(self.config)
            type_text("fill_in_application_information | _fill_phone_information_greenhouse_io | ok")
            
            # Fill location
            self._fill_location_greenhouse_io(self.config)
            type_text("fill_in_application_information | _fill_location_greenhouse_io | ok")
            
            # Upload resume
            self._upload_resume_greenhouse_io(self.config)
            type_text("fill_in_application_information | _upload_resume_greenhouse_io | ok")
            
            # Fill optional fields if required
            self._fill_optional_fields_greenhouse_io(self.config)
            type_text("fill_in_application_information | _fill_optional_fields_greenhouse_io | ok")
            
            # Fill dropdown questions
            self._fill_dropdown_questions_greenhouse_io(self.config)
            type_text("fill_in_application_information | _fill_dropdown_questions_greenhouse_io | ok")
            
            # Fill text questions
            self._fill_text_questions_greenhouse_io(self.config)
            type_text("fill_in_application_information | _fill_text_questions_greenhouse_io | ok")
            
            # Fill consent and acknowledgement
            self._fill_consent_acknowledgement_greenhouse_io(self.config)
            type_text("fill_in_application_information | _fill_consent_acknowledgement_greenhouse_io | ok")
            
            type_text("✅ fill_in_application_information | success!")
            type_text(f"\n{'='*50}")
            
            return True
            
         except Exception as e:
            type_text(f"🚫 ERROR | fill_in_application_information | Error filling application: {e}")
            raise
            
      else:
         type_text("🚫 ERROR | fill_in_application_information | Unsupported domain for application filling")
         return False
   
   # START - Supporting functions for greenhouse.io
   def _fill_basic_information_greenhouse_io(self, config):
      """Fill basic personal information fields"""
      try:
         # First Name
         first_name_field = self.driver.find_element(By.ID, "first_name")
         self.human_mouse_movement(self.driver.find_element(By.TAG_NAME, "body"), first_name_field)
         first_name_field.clear()
         self.human_typing(first_name_field, config.get('first_name', ''))
         type_text("    _fill_basic_information_greenhouse_io | first_name | ok")
         self.human_delay()
         
         # Last Name
         last_name_field = self.driver.find_element(By.ID, "last_name")
         self.human_mouse_movement(first_name_field, last_name_field)
         last_name_field.clear()
         self.human_typing(last_name_field, config.get('last_name', ''))
         type_text("    _fill_basic_information_greenhouse_io | last_name | ok")
         self.human_delay()
         
         # Email
         email_field = self.driver.find_element(By.ID, "email")
         self.human_mouse_movement(last_name_field, email_field)
         email_field.clear()
         self.human_typing(email_field, config.get('email', ''))
         type_text("    _fill_basic_information_greenhouse_io | email | ok")
         self.human_delay()
         
      except Exception as e:
         type_text(f"_fill_basic_information_greenhouse_io | Error: {e}")
         raise
   
   def _fill_phone_information_greenhouse_io(self, config):
      """Fill phone number information"""
      try:
         # Try to find and fill country code dropdown if it exists
         country_selectors = [
               "input[id*='country'][type='text']",
               "input[aria-label*='country' i]",
               "input[aria-labelledby*='country']",
               "div.select__container input[role='combobox']",
               "#country"
         ]
         
         country_found = False
         for selector in country_selectors:
               try:
                  country_dropdown = self.driver.find_element(By.CSS_SELECTOR, selector)
                  self.human_mouse_movement(self.driver.find_element(By.ID, "email"), country_dropdown)
                  country_dropdown.click()
                  self.human_delay()
                  
                  # Type country name or code from config, default to "United States"
                  country_value = config.get('country', 'United States')
                  country_dropdown.send_keys(country_value)
                  self.human_delay()
                  
                  # Press enter to select
                  country_dropdown.send_keys(Keys.RETURN)
                  self.human_delay()
                  country_found = True
                  break
               except:
                  continue
         
         if not country_found:
               type_text("⚠️ WARNING | _fill_phone_information_greenhouse_io | Country code dropdown not found, continuing without setting country")
         
         # Phone number field - try multiple selectors
         phone_selectors = [
               "input[id*='phone']",
               "input[type='tel']",
               "input[aria-label*='phone' i]",
               "input[aria-labelledby*='phone']",
               "#phone"
         ]
         
         phone_field = None
         for selector in phone_selectors:
               try:
                  phone_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                  break
               except:
                  continue
         
         if phone_field:
               self.human_mouse_movement(self.driver.find_element(By.ID, "email"), phone_field)
               phone_field.clear()
               self.human_typing(phone_field, config.get('phone', ''))
               self.human_delay()
         else:
               type_text("⚠️ WARNING | _fill_phone_information_greenhouse_io | Phone field not found")
               
      except Exception as e:
         type_text(f"_fill_phone_information_greenhouse_io | Error: {e}")
         # Don't raise, just log and continue
   
   def _fill_location_greenhouse_io(self, config):
      """Fill location information"""
      try:
         # Try the main location dropdown first
         try:
               location_dropdown = self.driver.find_element(By.ID, "candidate-location")
               self.human_mouse_movement(self.driver.find_element(By.ID, "phone"), location_dropdown)
               location_dropdown.click()
               self.human_delay()
               
               # Build location string from city and state
               city = config.get('city', '')
               state = config.get('state', '')
               location_string = f"{city}, {state}" if city and state else city
               
               # Type location (this will filter and select from dropdown)
               location_dropdown.send_keys(location_string)
               self.human_delay()
               
               # Press enter to select first matching option
               location_dropdown.send_keys(Keys.RETURN)
               self.human_delay()
               
         except:
               # If main location dropdown not found, try state-specific input
               type_text("    _fill_location_greenhouse_io | Main location dropdown not found, trying state input...")
               
               state_selectors = [
                  "input[id*='question_'][aria-label*='state' i]",
                  "input[aria-label*='state' i]",
                  "input[id*='state']",
                  "label:contains('state') + input"
               ]
               
               state_field = None
               for selector in state_selectors:
                  try:
                     state_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                     break
                  except:
                     continue
               
               if state_field:
                  self.human_mouse_movement(self.driver.find_element(By.TAG_NAME, "body"), state_field)
                  state_field.clear()
                  # Only fill state for this format
                  self.human_typing(state_field, config.get('state', ''))
                  self.human_delay()
                  type_text("    _fill_location_greenhouse_io | State field filled successfully")
               else:
                  type_text("⚠️ WARNING | _fill_location_greenhouse_io | No location or state field found")
                  
      except Exception as e:
         type_text(f"_fill_location_greenhouse_io | Error: {e}")
         # Don't raise, just log and continue
   
   def _upload_resume_greenhouse_io(self, config):
      """Upload resume file"""
      try:
         # Try multiple selectors for resume input
         resume_selectors = [
               "input[id='resume'][type='file']",
               "input[id*='resume']",
               "input[type='file']",
               "input[accept*='.pdf']",
               "input[accept*='.doc']"
         ]
         
         resume_input = None
         for selector in resume_selectors:
               try:
                  resume_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                  break
               except:
                  continue
         
         if not resume_input:
               raise Exception("🚫 RESUME_NOT_FOUND | No resume input field found on the page")
         
         # Use a safe starting element for mouse movement
         safe_start_elements = [
               "input[id*='phone']",
               "input[id*='email']", 
               "input[type='tel']",
               "body"
         ]
         
         start_element = None
         for selector in safe_start_elements:
               try:
                  start_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                  break
               except:
                  continue
         
         if start_element:
               self.human_mouse_movement(start_element, resume_input)
         else:
               # Fallback to direct click if no safe start element found
               resume_input.click()
         
         # Get resume file path from config
         resume_path = config.get('resume_path', '')
         if resume_path and os.path.exists(resume_path):
               resume_input.send_keys(resume_path)
               type_text("    _upload_resume_greenhouse_io | Resume uploaded successfully")
         else:
               raise Exception(f"🚫 RESUME_FILE_NOT_FOUND | Resume file not found at path: {resume_path}")
               
         self.human_delay()
         
      except Exception as e:
         if "RESUME_NOT_FOUND" in str(e) or "RESUME_FILE_NOT_FOUND" in str(e):
               type_text(f"🚫 ERROR | _upload_resume_greenhouse_io | {e}")
               raise
         else:
               type_text(f"_upload_resume_greenhouse_io | Error: {e}")
               raise
   
   def _fill_optional_fields_greenhouse_io(self, config):
      """Fill optional fields only if they are required (have asterisk)"""
      if config.get('linkedin_url', '') == "":
         type_text("WARNING | _fill_optional_fields_greenhouse_io | You have not specified a linkedin url. Sometimes this isn't required, which is why this is a warning.")
      
      try:
         # More specific selectors for LinkedIn field
         linkedin_selectors = [
               "input#question_4201125009",  # Exact ID match
               "input[id='question_4201125009']",  # Exact ID match alternative
               "input[id*='question_4201125009']",  # Contains this ID
               "input[aria-label*='LinkedIn Profile']",  # Exact aria-label match
               "input[aria-label*='LinkedIn']",  # Partial aria-label match
         ]
         
         for selector in linkedin_selectors:
               try:
                  linkedin_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                  
                  # Check if required using multiple methods
                  field_id = linkedin_field.get_attribute('id')
                  is_required = False
                  
                  # Method 1: Check label for asterisk
                  if field_id:
                     try:
                           label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{field_id}']")
                           if '*' in label.text:
                              is_required = True
                     except:
                           pass
                  
                  # Method 2: Check aria-required attribute
                  if not is_required and linkedin_field.get_attribute('aria-required') == 'true':
                     is_required = True
                  
                  # Method 3: Check for required class or attributes
                  if not is_required and ('required' in linkedin_field.get_attribute('class') or 
                                       linkedin_field.get_attribute('required') is not None):
                     is_required = True
                  
                  if is_required:
                     self.human_mouse_movement(self.driver.find_element(By.TAG_NAME, "body"), linkedin_field)
                     linkedin_field.click()
                     linkedin_field.clear()
                     linkedin_url = config.get('linkedin', config.get('linkedin_url', ''))
                     self.human_typing(linkedin_field, linkedin_url)
                     self.human_delay()
                     type_text("_fill_optional_fields_greenhouse_io | LinkedIn field filled (required)")
                     return
                  else:
                     type_text("_fill_optional_fields_greenhouse_io | LinkedIn field found but not required - skipping")
                     return
                     
               except Exception as e:
                  continue
                     
         type_text("_fill_optional_fields_greenhouse_io | No LinkedIn field found or not required")
                     
      except Exception as e:
         type_text(f"_fill_optional_fields_greenhouse_io | Error: {e}")
      
   def _fill_dropdown_questions_greenhouse_io(self, config):
      """Fill all dropdown questions using keyword matching"""
      # Define field mappings with flexible keyword matching
      field_mappings = [
         {
               "config_key": "source",
               "keywords": ["how did you hear", "how you hear", "referral source", "source", "found this job"],
               "fallback_value": "LinkedIn"  # Common default
         },
         {
               "config_key": "is_18_or_older",
               "keywords": ["18 or older", "are you 18", "at least 18", "age requirement"],
               "fallback_value": "Yes"
         },
         {
               "config_key": "work_eligible",
               "keywords": ["work authorization", "work eligible", "authorized to work", "eligible to work", "employment authorization"],
               "fallback_value": "Yes"
         },
         {
               "config_key": "requires_sponsorship",
               "keywords": ["sponsorship", "visa sponsorship", "require sponsorship", "h-1b", "h1b", "tn visa", "e-3 visa", "employment visa"],
               "fallback_value": "No"
         },
         {
               "config_key": "us_citizen",
               "keywords": ["us citizen", "u.s. citizen", "citizenship", "permanent resident", "green card"],
               "fallback_value": "Yes"  # Adjust based on your situation
         },
         {
               "config_key": "education_level",
               "keywords": ["education", "highest level", "completed education", "degree", "educational background"],
               "fallback_value": "Bachelor's Degree"  # Common default
         },
         {
               "config_key": "text_consent",
               "keywords": ["text message", "sms", "text consent", "mobile message"],
               "fallback_value": "No"  # Usually opt for privacy
         },
         {
               "config_key": "truth_statement",
               "keywords": ["certify", "truth", "accurate", "complete", "authorize investigation", "background check"],
               "fallback_value": "Yes"
         }
      ]
      
      filled_count = 0
      total_attempted = 0
      
      for field_info in field_mappings:
         config_key = field_info["config_key"]
         config_value = config.get(config_key, '').strip()
         
         # Skip if no value provided in config
         if not config_value:
               type_text(f"_fill_dropdown_questions_greenhouse_io | No value provided for '{config_key}' - skipping")
               continue
               
         total_attempted += 1
         
         try:
               # Try to find and fill the dropdown
               success = self._find_and_fill_dropdown_by_keywords_greenhouse_io(
                  field_info["keywords"], 
                  config_value,
                  field_info.get("fallback_value")
               )
               
               if success:
                  filled_count += 1
                  self.human_delay()
               else:
                  type_text(f"_fill_dropdown_questions_greenhouse_io | Could not find dropdown for '{config_key}'")
                  
         except Exception as e:
               type_text(f"_fill_dropdown_questions_greenhouse_io | Error with '{config_key}': {e}")
               continue
      
      type_text(f"_fill_dropdown_questions_greenhouse_io | Successfully filled {filled_count}/{total_attempted} dropdown fields")

   def _find_and_fill_dropdown_by_keywords_greenhouse_io(self, keywords, value, fallback_value=None):
      """Find dropdown by label keywords and fill it"""
      # First, try to find all dropdown containers
      dropdown_selectors = [
         "div.select__container",
         "div.select-shell",
         "div[class*='select']",
         "div.field",
         "div.application-field"
      ]
      
      for selector in dropdown_selectors:
         try:
               containers = self.driver.find_elements(By.CSS_SELECTOR, selector)
               for container in containers:
                  if self._container_matches_keywords_greenhouse_io(container, keywords):
                     return self._fill_dropdown_container_greenhouse_io(container, value, fallback_value)
         except:
               continue
      
      return False

   def _container_matches_keywords_greenhouse_io(self, container, keywords):
      """Check if container contains any of the target keywords"""
      try:
         # Get all text from container and its children
         container_text = container.text.lower()
         
         # Also check label text specifically
         label_text = ""
         try:
            label = container.find_element(By.CSS_SELECTOR, "label")
            label_text = label.text.lower()
         except:
            pass
         
         # Also check aria-label attributes
         aria_labels = ""
         try:
            inputs = container.find_elements(By.CSS_SELECTOR, "[aria-label]")
            for input_elem in inputs:
               aria_labels += " " + input_elem.get_attribute("aria-label").lower()
         except:
               pass
         
         combined_text = f"{container_text} {label_text} {aria_labels}"
         
         # Check if any keyword matches
         for keyword in keywords:
            if keyword.lower() in combined_text:
               type_text(f"_fill_dropdown_questions_greenhouse_io | Found dropdown matching keyword: '{keyword}'")
               return True
                  
      except Exception as e:
         type_text(f"_container_matches_keywords_greenhouse_io | Error checking container: {e}")
      
      return False
   
   def _fill_dropdown_container_greenhouse_io(self, container, value, fallback_value=None):
      """Fill a found dropdown container"""
      try:
         # Try different ways to find the dropdown input/button
         dropdown_selectors = [
               "input[type='text']",
               "div.select__control",
               "button[aria-haspopup='listbox']",
               ".select__input",
               "[role='combobox']"
         ]
         
         dropdown_element = None
         
         for selector in dropdown_selectors:
            try:
               dropdown_element = container.find_element(By.CSS_SELECTOR, selector)
               break
            except:
               continue
         
         if not dropdown_element:
            type_text("_fill_dropdown_container_greenhouse_io | Could not find dropdown element in container")
            return False
         
         # Click to open dropdown
         self.human_mouse_movement(container, dropdown_element)
         dropdown_element.click()
         self.human_delay()
         
         # Now look for the option to select
         option_selectors = [
            f"div[role='option']:contains('{value}')",
            f"li[role='option']:contains('{value}')",
            f"*[role='option']:contains('{value}')"
         ]
         
         option_found = False
         
         for selector in option_selectors:
            try:
               # Use XPath for contains text matching since CSS doesn't support :contains
               options = self.driver.find_elements(By.XPATH, f"//*[@role='option' and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{value.lower()}')]")
               if options:
                  self.human_mouse_movement(dropdown_element, options[0])
                  options[0].click()
                  option_found = True
                  break
            except:
               continue
         
         # If exact value not found, try fallback
         if not option_found and fallback_value:
            type_text(f"_fill_dropdown_container_greenhouse_io | Exact value '{value}' not found, trying fallback: '{fallback_value}'")
            for selector in option_selectors:
               try:
                  options = self.driver.find_elements(By.XPATH, f"//*[@role='option' and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{fallback_value.lower()}')]")
                  if options:
                        self.human_mouse_movement(dropdown_element, options[0])
                        options[0].click()
                        option_found = True
                        break
               except:
                  continue
         
         if option_found:
               type_text(f"_fill_dropdown_container_greenhouse_io | Successfully selected: '{value}'")
               return True
         else:
               type_text(f"_fill_dropdown_container_greenhouse_io | Could not find option for: '{value}'")
               return False
               
      except Exception as e:
         type_text(f"_fill_dropdown_container_greenhouse_io | Error filling dropdown: {e}")
         return False
   
   def _select_dropdown_option_greenhouse_io(self, field_id, value):
      """Select an option from a dropdown"""
      try:
         dropdown = self.driver.find_element(By.ID, field_id)
         self.human_mouse_movement(self.driver.find_element(By.TAG_NAME, "body"), dropdown)
         dropdown.click()
         self.human_delay()
         
         # Type the value to filter options
         dropdown.send_keys(value)
         self.human_delay()
         
         # Press enter to select
         dropdown.send_keys(Keys.RETURN)
         self.human_delay()
         
      except Exception as e:
         type_text(f"_select_dropdown_option_greenhouse_io | Error with {field_id}: {e}")
         raise
   
   def _fill_text_questions_greenhouse_io(self, config):
      """Fill text-based questions"""
      text_mappings = {
         "question_4346839009": "desired_salary",  # Desired salary
         "question_4346840009": "start_date"  # Available start date
      }
      
      for field_id, config_key in text_mappings.items():
         try:
               text_field = self.driver.find_element(By.ID, field_id)
               self.human_mouse_movement(self.driver.find_element(By.TAG_NAME, "body"), text_field)
               text_field.clear()
               
               # Handle start_date conversion from weeks to actual date
               if config_key == "start_date":
                  weeks_ahead = config.get(config_key, 0)
                  start_date = self._calculate_start_date(weeks_ahead)
                  self.human_typing(text_field, start_date)
               else:
                  self.human_typing(text_field, config.get(config_key, ''))
                  
               self.human_delay()
         except Exception as e:
               type_text(f"_fill_text_questions_greenhouse_io | Error with {field_id}: {e}")
               continue
   
   def _calculate_start_date(self, weeks_ahead):
      """Calculate start date based on weeks ahead from today"""
      from datetime import datetime, timedelta
      
      # Calculate target date
      target_date = datetime.now() + timedelta(weeks=weeks_ahead)
      
      # Format as MM/DD/YYYY (common US date format)
      return target_date.strftime("%m/%d/%Y")
   
   def _fill_consent_acknowledgement_greenhouse_io(self, config):
      """Fill consent and acknowledgement fields"""
      selectors = [
         "input[id*='question_4346842009']",
         "input[name*='privacy']",
         "input[type='checkbox']",
         ".consent-checkbox",
         "[data-qa='consent-checkbox']"
      ]
      
      for selector in selectors:
         try:
               privacy_checkbox = self.driver.find_element(By.CSS_SELECTOR, selector)
               self.human_mouse_movement(self.driver.find_element(By.TAG_NAME, "body"), privacy_checkbox)
               
               if not privacy_checkbox.is_selected():
                  privacy_checkbox.click()
                  
               self.human_delay()
               type_text("    _fill_consent_acknowledgement_greenhouse_io | Consent acknowledged")
               return True
               
         except NoSuchElementException:
               type_text("    _fill_consent_acknowledgement_greenhouse_io | WARNING | Element not found")
               continue
         except Exception as e:
               type_text(f"_fill_consent_acknowledgement_greenhouse_io | Error with selector {selector}: {e}")
               continue
      
      type_text("_fill_consent_acknowledgement_greenhouse_io | No consent box found - continuing")
      return False
   # STOP - Supporting functions for greenhouse.io
   
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
   
   def detect_security_clearance(self):
      """
      Scan HTML page content for DoD security clearance requirements
      Returns one of: "None", "Confidential", "Secret", "Top Secret", "Top Secret with Polygraph"
      """
      try:
         # Get the entire page HTML content
         page_html = self.driver.page_source.lower()
         
         # Define clearance terms with specific patterns to minimize false positives
         clearance_terms = {
               "Top Secret with Polygraph": [
                  r"top\s*secret.*polygraph",
                  r"ts.*sci.*poly",
                  r"top\s*secret.*sci.*poly",
                  r"ts/sci.*polygraph",
                  r"polygraph.*top\s*secret",
                  r"full\s*scope.*polygraph",
                  r"fsp.*ts/sci",
                  r"ts/sci.*fsp"
               ],
               "Top Secret": [
                  r"\btop\s*secret\b",
                  r"\bts/sci\b",
                  r"\bts\s*clearance\b",
                  r"top\s*secret.*clearance",
                  r"requires.*top\s*secret",
                  r"must.*have.*top\s*secret",
                  r"active.*top\s*secret",
               ],
               "Secret": [
                  r"\bsecret\s*clearance\b",
                  r"requires.*secret",
                  r"must.*have.*secret",
                  r"active.*secret",
                  r"\bsecret.*level",
                  r"dod.*secret"
               ],
               "Confidential": [
                  r"\bconfidential\s*clearance\b",
                  r"requires.*confidential",
                  r"must.*have.*confidential",
                  r"active.*confidential"
               ],
               "Public Trust": [
                  r"public\s*trust",
                  r"public\s*trust.*clearance",
                  r"requires.*public\s*trust",
                  r"public\s*trust.*position",
                  r"public\s*trust.*level"
               ]
         }
         
         # Check for each clearance level in order of highest to lowest
         clearance_levels = [
               "Top Secret with Polygraph",
               "Top Secret", 
               "Secret",
               "Confidential",
               "Public Trust"
         ]
         
         detected_clearance = "None"
         
         for level in clearance_levels:
               for pattern in clearance_terms[level]:
                  if re.search(pattern, page_html, re.IGNORECASE):
                     detected_clearance = level
                     type_text(f"  Security Clearance: Detected '{level}' with pattern: {pattern}")
                     return detected_clearance
         
         return detected_clearance
         
      except Exception as e:
         type_text(f"  Error detecting security clearance: {e}")
         return "None"
   
   def compare_clearance_from_config(self, detected_clearance):
      """
      Purpose: Compares the clearance from the user's config file to that of the job listing
      Inputs:
         detected_clearance: string, the clearance level that was detected in the job listing
      Returns:
         True if user meets clearance requirement, False otherwise
      """
      try:
         # Get clearance from config
         config_clearance = self.config.get('clearance', 'none').lower()
         detected_clearance = detected_clearance.lower()
         
         # Define clearance hierarchy (lowest to highest)
         clearance_hierarchy = {
               "none": 0,
               "public trust": 1,
               "confidential": 2,
               "secret": 3,
               "top secret": 4,
               "top secret with polygraph": 5
         }
         
         # Get numeric values for comparison
         config_level = clearance_hierarchy.get(config_clearance, 0)
         detected_level = clearance_hierarchy.get(detected_clearance, 0)
         
         type_text(f"  Clearance Check: User has '{config_clearance}' ({config_level}), job requires '{detected_clearance}' ({detected_level})")
         
         # User meets requirement if their clearance level >= job requirement level
         if config_level >= detected_level:
               type_text(f"  ✓ User meets clearance requirement")
               return True
         else:
               type_text(f"  ✗ User does NOT meet clearance requirement")
               return False
               
      except Exception as e:
         type_text(f"  Error comparing clearance levels: {e}")
         return True  # Default to True if there's an error to avoid filtering out jobs unnecessarily
   
   def print_statistics(self):
      type_text("")
      print_applybot_mascot_w_statistics() # Print the mascot with statistics text
      type_text("")
      self.get_xpath_statistics()
      type_text("")
      self.get_element_scraping_statistics()
      type_text("")
      self.get_security_clearance_statistics()
   
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
         normalized_links.append(link)
   
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
      Purpose: Sorts the links in the CSV file input by their domain alphabetically, removes duplicates and normalizes links. This is so that ApplyBot can handle different platforms such as LinkedIn and Indeed separately
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
      # Normalize the links to remove fluff and tracking
      normalized_job_links = normalize_job_links(unique_links)
      # Remove duplicates again after normalization to remove trickier duplicates
      final_unique = remove_duplicate_links(normalized_job_links)
      
      # Extract domain from each URL and create tuples of (domain, url)
      domain_url_pairs = []
      for url in final_unique:
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
      Returns a tuple such that:
         normalized salary string or "?" for unknown values
         original text, or explanation for when it could not parse
   """
   
   # Handle null/None values and convert to string first
   if pay_rate_text is None or pay_rate_text == "?" or (isinstance(pay_rate_text, str) and pay_rate_text.strip() == "") or pd.isna(pay_rate_text):
      return ("?", "Could not find or parse pay rate. ")
   
   text = str(pay_rate_text).lower().strip()
   
   # Check for empty string after stripping
   if text == "":
      return ("?", "Could not find or parse pay rate. ")
   
   # Check for non-salary keywords after conversion (for when it grabs the wrong information, typically when the place it looks for the pay rate does not exist)
   if any(keyword in text for keyword in ["hybrid", "on-site", "site", "remote", "full-time", "full", "part", "part-time", "time"]):
      return ("?", "Could not find or parse pay rate.")
   
   # Handle the specific case of "$30/yr" typo (likely meant $30/hr)
   if re.search(r'\$\s*(\d+[.,]?\d*)\s*/?\s*yr', text) and not re.search(r'k\s*/?\s*yr', text):
      # Extract the numeric value and assume it was meant to be per hour
      match = re.search(r'\$\s*(\d+[.,]?\d*)\s*/?\s*yr', text)
      if match:
         hourly_rate = float(match.group(1).replace(',', ''))
         # Only convert if it's an unreasonably low annual salary (likely typo)
         if hourly_rate < 100:  # Assuming annual salaries under $100 are typos
               annual_salary = hourly_rate * 40 * 52  # 40 hrs/week * 52 weeks
               return (f"${annual_salary:,.0f}", text)
   
   # Handle hourly rates (single or range)
   hourly_matches = re.findall(r'\$\s*(\d+[.,]?\d*)\s*/?\s*hr\b', text)
   if hourly_matches:
      if len(hourly_matches) == 1: # Single hourly rate
         hourly_rate = float(hourly_matches[0].replace(',', ''))
         annual_salary = hourly_rate * 40 * 52
         return (f"${annual_salary:,.0f}", text)
      elif len(hourly_matches) >= 2: # Handle multiple hourly rates (take first two as range, hourly wage -> salary midpoint)
         hourly_low = float(hourly_matches[0].replace(',', ''))
         hourly_high = float(hourly_matches[1].replace(',', ''))
         annual_low = hourly_low * 40 * 52
         annual_high = hourly_high * 40 * 52
         midpoint = (annual_low + annual_high) / 2
         midpoint_rounded = round(midpoint)  # Don't round to nearest thousand for hourly ranges
         note = f"Original range: ${annual_low:,.0f}/yr - ${annual_high:,.0f}/yr"
         return (f"${midpoint_rounded:,.0f}", note)
   
   # Handle annual ranges with K notation first (before individual K matches)
   k_range_pattern = r'\$\s*(\d+[.,]?\d*)\s*k\s*/?\s*yr\s*[-–—]\s*\$\s*(\d+[.,]?\d*)\s*k\s*/?\s*yr'
   k_range_match = re.search(k_range_pattern, text)
   if k_range_match:
      annual_low = float(k_range_match.group(1).replace(',', '')) * 1000
      annual_high = float(k_range_match.group(2).replace(',', '')) * 1000
      midpoint = (annual_low + annual_high) / 2
      midpoint_rounded = round(midpoint)
      note = f"Original range: ${annual_low:,.0f}/yr - ${annual_high:,.0f}/yr"
      return (f"${midpoint_rounded:,.0f}", note)
   
   # Handle annual salaries with K notation (individual)
   k_match = re.search(r'\$\s*(\d+[.,]?\d*)\s*k\s*/?\s*yr', text)
   if k_match:
      annual_salary = float(k_match.group(1).replace(',', '')) * 1000
      return (f"${annual_salary:,.0f}", text)
   
   # Handle annual ranges - improved detection
   # Look for ranges with explicit separators
   # Salary range -> salary midpoint
   range_pattern = r'\$\s*(\d{1,3}(?:[,.]?\d{3})*(?:[.,]\d+)?)\s*(?:/?\s*yr)?\s*[-–—]\s*\$\s*(\d{1,3}(?:[,.]?\d{3})*(?:[.,]\d+)?)\s*(?:/?\s*yr)?'
   annual_range_match = re.search(range_pattern, text)
   if annual_range_match:
      annual_low_str = annual_range_match.group(1).replace(',', '').replace('.', '')
      annual_high_str = annual_range_match.group(2).replace(',', '').replace('.', '')
      annual_low = int(annual_low_str)
      annual_high = int(annual_high_str)
      midpoint = (annual_low + annual_high) / 2
      note = f"Original range: ${annual_low:,.0f}/yr - ${annual_high:,.0f}/yr"
      return (f"${midpoint:,.0f}", note)
   
   # Handle explicit annual salaries - improved pattern
   annual_match = re.search(r'\$\s*(\d{1,3}(?:[,.]?\d{3})*(?:[.,]\d+)?)\s*/?\s*yr', text)
   if annual_match:
      annual_salary_str = annual_match.group(1).replace(',', '').replace('.', '')
      # Handle cases where there might be decimal points in the number
      if '.' in annual_match.group(1):
         annual_salary = float(annual_match.group(1).replace(',', ''))
      else:
         annual_salary = int(annual_salary_str)
      return (f"${annual_salary:,.0f}", text)
   
   # Handle annual ranges - improved detection
   # Look for ranges with explicit separators
   # Salary range -> salary midpoint
   range_pattern = r'\$\s*(\d{1,3}(?:[,.]?\d{3})*(?:[.,]\d+)?)\s*/?\s*yr\s*[-–—]\s*\$\s*(\d{1,3}(?:[,.]?\d{3})*(?:[.,]\d+)?)\s*/?\s*yr'
   annual_range_match = re.search(range_pattern, text)
   if annual_range_match:
      annual_low_str = annual_range_match.group(1).replace(',', '').replace('.', '')
      annual_high_str = annual_range_match.group(2).replace(',', '').replace('.', '')
      annual_low = int(annual_low_str)
      annual_high = int(annual_high_str)
      midpoint = (annual_low + annual_high) / 2
      note = f"Original range: ${annual_low:,.0f}/yr - ${annual_high:,.0f}/yr"
      return (f"${midpoint:,.0f}", note)
   
   # Handle simple annual ranges without /yr (like "$45,600 - $80,000")
   simple_range_match = re.search(r'\$\s*(\d{1,3}(?:[,.]?\d{3})+)\s*[-–—]\s*\$\s*(\d{1,3}(?:[,.]?\d{3})+)', text)
   if simple_range_match:
      annual_low_str = simple_range_match.group(1).replace(',', '').replace('.', '')
      annual_high_str = simple_range_match.group(2).replace(',', '').replace('.', '')
      annual_low = int(annual_low_str)
      annual_high = int(annual_high_str)
      midpoint = (annual_low + annual_high) / 2
      midpoint_rounded = round(midpoint)  # Round to nearest dollar
      note = f"Original range: ${annual_low:,.0f} - ${annual_high:,.0f}"
      return (f"${midpoint_rounded:,.0f}", note)
   
   # Also handle simple annual numbers without /yr that look like salaries
   simple_annual_match = re.search(r'^\s*\$\s*(\d{3,})\s*$', text)
   if simple_annual_match:
      annual_salary = int(simple_annual_match.group(1))
      return (f"${annual_salary:,.0f}", text)
   
   # Handle "up to" hourly rates
   upto_match = re.search(r'up\s+to\s+\$\s*(\d+[.,]?\d*)\s*/?\s*hr', text)
   if upto_match:
      hourly_rate = float(upto_match.group(1).replace(',', ''))
      annual_salary = hourly_rate * 40 * 52
      return (f"${annual_salary:,.0f}", text)
   
   # Handle "starting at" formats
   starting_match = re.search(r'starting\s+at\s+\$\s*(\d+[.,]?\d*)\s*k\s*/?\s*yr', text)
   if starting_match:
      annual_salary = float(starting_match.group(1).replace(',', '')) * 1000
      return (f"${annual_salary:,.0f}", text)
   
   # If no patterns match but it's not "?", return original
   if text != "?":
      return (text, "Could not re-format pay rate.")
   
   return ("?", "Could not find or parse pay rate.")

def normalize_pay_rate_csv(csv_file_path):
   "DEPRECATED, WILL NEED ADJUSTING BEFORE IT WILL WORK CORRECTLY!"

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
   
   # Initialize ApplyBot (will call setup_driver, which will open browser)
   ApplyBot = ApplyBot(config=config, headless=args.headless)
   
   # Login manually if needed
   ApplyBot.linkedin_login()
   
   # Prepare output CSV
   fieldnames = ['Job Title', 'Employer', 'Location', 'Pay Rate', 'Job Ad', 'Date Found', 'Notes', 'Security Clearance']
   
   try:
      with open(args.output_csv, 'w', newline='', encoding='utf-8') as csvfile:
         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
         writer.writeheader()
         
         successful_scrapes = 0
         failed_links = []
         incompatible_links = [] # Job links whose requirements are incompatible with the user
         
         for i, link in enumerate(cleaned_links, 1):
            type_text(f"\n{'='*50}") # Divider
            type_text(f"\nProcessing link {i}/{len(cleaned_links)}")
            
            # Scrape the job info
            job_info = ApplyBot.scrape_job_info(link)
            
            if job_info and job_info != "incompatible":  # ← CHECK FOR INCOMPATIBLE EXPLICITLY
               writer.writerow(job_info)
               csvfile.flush()  # Ensure data is written immediately
               successful_scrapes += 1
               type_text(f"✅ Successfully scraped and saved")
            elif job_info == "incompatible":  # ← HANDLE INCOMPATIBLE CASE
               incompatible_links.append(link) # Adds the link to the list of incompatible job listing links
               type_text(f"🚫 Job incompatible - skipped due to clearance requirements")
            else: # Actual failure case (job_info is None), requires user input
               failed_links.append(link)
               type_text(f"🚫 Failed to scrape")
               
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
      type_text(f" ✅ Successful: {successful_scrapes}")
      type_text(f" 🚫 Failed: {len(failed_links)}")
      type_text(f"Output saved to: {args.output_csv}")
      
      # Show any links that failed to be scraped
      if failed_links:
         type_text(f"\nFailed links:")
         for link in failed_links:
               type_text(f"  - {link}")
      
      # Post Processing
      type_text(f"\n{'='*50}") # Divider
      
      # Start to apply to jobs that passed initial scraping and requirements
      # TODO
   
   except Exception as e:
      type_text(f"\n{'='*50}") # Divider
      type_text(f"🚫 Unexpected error: {e}")
      type_text("Press Enter to exit...")
      input()
   finally:
      ApplyBot.close()



if __name__ == "__main__":
   #main()
   
   # TESTING ONLY
   parser = argparse.ArgumentParser(description='Scrape job information from links')
   parser.add_argument('--config', default='config.json', help='Config file path')
   args = parser.parse_args()
   
   link = "https://job-boards.greenhouse.io/roadrunner/jobs/4031672009"
   
   # Intro
   type_text(f"\n{'='*50}")
   type_text("") # Divider
   print_applybot_intro()
   
   # Fetch config file contents
   type_text(f"\n{'='*50}")
   type_text("") # Divider
   config = load_config(args.config)
   
   # Initialize ApplyBot (will call setup_driver, which will open browser)
   ApplyBot = ApplyBot(config=config)
   
   ApplyBot.fill_in_application_information(link)