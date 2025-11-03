import unittest
import os
import csv
import pandas as pd
import re
import sys
import tempfile
from urllib.parse import urlparse
from unittest.mock import patch, MagicMock
from main import pre_process_job_links, read_job_links, remove_duplicate_links, normalize_pay_rate, type_text, print_applybot_mascot_w_statistics

# # Import the functions from your main module
# # Assuming they are in a file called job_preparation.py
# from main import sort_job_links_by_domain, read_job_links, remove_duplicate_links

# class TestJobListingPreparation(unittest.TestCase):
#    def setUp(self):
#       """Set up test CSV files before each test"""
#       self.test_csv_az = 'test_links_az.csv'
#       self.test_csv_za = 'test_links_za.csv'
#       self.test_csv_edge = 'test_links_edge.csv'
#       self.test_csv_empty = 'test_links_empty.csv'
      
#       # Test data for A-Z sorting
#       az_links = [
#          'https://apple.com/jobs/123',
#          'https://beta.company.com/jobs/456',
#          'https://alpha.org/careers/789',
#          'https://google.com/positions/101',
#          'https://microsoft.com/careers/112'
#       ]
      
#       # Test data for Z-A sorting (includes duplicates)
#       za_links = [
#          'https://zebra.com/jobs/1',
#          'https://yahoo.com/careers/2',
#          'https://xerox.com/positions/3',
#          'https://yahoo.com/careers/2',  # duplicate
#          'https://uber.com/jobs/4'
#       ]
      
#       # Test data for edge cases
#       edge_links = [
#          'https://www.linkedin.com/jobs/view/123',  # with www
#          'https://linkedin.com/jobs/view/456',      # without www
#          'invalid-url',                             # malformed URL
#          '',                                        # empty string
#          'https://indeed.com/job/789',
#          'http://mixed-protocol.org/jobs/101',      # http instead of https
#          'https://www.indeed.com/job/987'           # another with www
#       ]
      
#       # Create test CSV files
#       self._create_test_csv(self.test_csv_az, az_links)
#       self._create_test_csv(self.test_csv_za, za_links)
#       self._create_test_csv(self.test_csv_edge, edge_links)
#       self._create_test_csv(self.test_csv_empty, [])
   
#    def tearDown(self):
#       """Clean up test files after each test"""
#       for file_path in [self.test_csv_az, self.test_csv_za, self.test_csv_edge, self.test_csv_empty]:
#          if os.path.exists(file_path):
#                os.remove(file_path)
   
#    def _create_test_csv(self, file_path, links):
#       """Helper method to create test CSV files"""
#       with open(file_path, 'w', newline='', encoding='utf-8') as file:
#          writer = csv.writer(file)
#          for link in links:
#                writer.writerow([link])
   
#    def test_sort_az_alphabetically(self):
#       """Test sorting links by domain in A-Z order"""
#       result = sort_job_links_by_domain(self.test_csv_az, ascending_alphabetically=True)
      
#       # Extract domains for verification
#       domains = []
#       for url in result:
#          try:
#                parsed = urlparse(url)
#                domain = parsed.netloc.lower()
#                if domain.startswith('www.'):
#                   domain = domain[4:]
#                domains.append(domain)
#          except:
#                domains.append('')
      
#       # Check if domains are sorted A-Z
#       expected_domains = sorted(domains)
#       self.assertEqual(domains, expected_domains, "Domains should be sorted A-Z")
      
#       # Verify specific order
#       expected_order = [
#          'https://alpha.org/careers/789',
#          'https://apple.com/jobs/123',
#          'https://beta.company.com/jobs/456',
#          'https://google.com/positions/101',
#          'https://microsoft.com/careers/112'
#       ]
#       self.assertEqual(result, expected_order, "Links should be sorted by domain A-Z")
   
#    def test_sort_za_alphabetically(self):
#       """Test sorting links by domain in Z-A order"""
#       result = sort_job_links_by_domain(self.test_csv_za, ascending_alphabetically=False)
      
#       # Extract domains for verification
#       domains = []
#       for url in result:
#          try:
#                parsed = urlparse(url)
#                domain = parsed.netloc.lower()
#                if domain.startswith('www.'):
#                   domain = domain[4:]
#                domains.append(domain)
#          except:
#                domains.append('')
      
#       # Check if domains are sorted Z-A
#       expected_domains = sorted(domains, reverse=True)
#       self.assertEqual(domains, expected_domains, "Domains should be sorted Z-A")
      
#       # Verify specific order and duplicate removal
#       expected_order = [
#          'https://zebra.com/jobs/1',
#          'https://yahoo.com/careers/2',  # duplicate should be removed
#          'https://xerox.com/positions/3',
#          'https://uber.com/jobs/4'
#       ]
#       self.assertEqual(result, expected_order, "Links should be sorted by domain Z-A and duplicates removed")
   
#    def test_edge_cases(self):
#       """Test sorting with edge cases including malformed URLs, empty strings, and www prefixes"""
#       result = sort_job_links_by_domain(self.test_csv_edge, ascending_alphabetically=True)
      
#       # The function should handle:
#       # - URLs with www prefix (should be normalized)
#       # - Malformed URLs
#       # - Empty strings
#       # - Duplicate domains with different protocols or www prefixes
      
#       # Verify that www domains are normalized (linkedin.com and www.linkedin.com should be treated the same)
#       linkedin_count = 0
#       indeed_count = 0
      
#       for url in result:
#          if 'linkedin' in url:
#                linkedin_count += 1
#          if 'indeed' in url:
#                indeed_count += 1
      
#       # Should have both linkedin URLs (they are different URLs even if same domain)
#       self.assertEqual(linkedin_count, 2, "Should preserve both linkedin URLs")
#       self.assertEqual(indeed_count, 2, "Should preserve both indeed URLs")
      
#       # Verify malformed URL and empty string are handled
#       self.assertIn('invalid-url', result, "Should handle malformed URLs")
      
#       # Check that empty strings are filtered out (based on read_job_links behavior)
#       self.assertNotIn('', result, "Empty strings should be filtered out")
   
#    def test_empty_file(self):
#       """Test sorting with an empty CSV file"""
#       result = sort_job_links_by_domain(self.test_csv_empty, ascending_alphabetically=True)
#       self.assertEqual(result, [], "Empty file should return empty list")
   
#    def test_duplicate_removal(self):
#       """Test that duplicates are removed before sorting"""
#       # Create a CSV with duplicates
#       duplicate_links = [
#          'https://example.com/job1',
#          'https://test.com/job2',
#          'https://example.com/job1',  # duplicate
#          'https://alpha.com/job3'
#       ]
      
#       self._create_test_csv('test_duplicates.csv', duplicate_links)
      
#       result_az = sort_job_links_by_domain('test_duplicates.csv', ascending_alphabetically=True)
      
#       # Check that duplicates are removed
#       self.assertEqual(len(result_az), 3, "Duplicates should be removed")
#       self.assertEqual(result_az.count('https://example.com/job1'), 1, "Should have only one instance of duplicate")
      
#       # Clean up
#       if os.path.exists('test_duplicates.csv'):
#          os.remove('test_duplicates.csv')


class TestNormalizePayRate(unittest.TestCase):
   
   def test_work_location_keywords_return_question_mark(self):
      """Test that work location/type keywords return '?'"""
      location_cases = [
         "hybrid work environment",
         "ON-SITE position",
         "remote work available",
         "FULL-TIME role",
         "part time job",
         "full time with benefits",
         "part-time contract",
         "must work on site",
         "HYBRID schedule",
         "REMOTE okay"
      ]
      for case in location_cases:
         with self.subTest(case=case):
               result = normalize_pay_rate(case)
               self.assertEqual(result[0], "?")
   
   def test_missing_or_unknown_values(self):
      """Test handling of missing/unknown values"""
      self.assertEqual(normalize_pay_rate("?")[0], "?")
      self.assertEqual(normalize_pay_rate("")[0], "?")
      self.assertEqual(normalize_pay_rate(None)[0], "?")
   
   def test_single_hourly_rates(self):
      """Test single hourly rate conversions"""
      test_cases = [
         ("$37 an hour", "$76,960"), 
         ("$37 hour", "$76,960"), 
         ("$37/hour", "$76,960"), 
         ("$37 / hour", "$76,960"), 
         ("$25/hr", "$52,000"),
         ("$15.50 /hr", "$32,240"),
         ("$100.75/hr", "$209,560"),
         ("$\t30/hr", "$62,400"),
         ("$ 45 / hr", "$93,600"),
         ("$0.50/hr", "$1,040"),
      ]
      for input_text, expected in test_cases:
         with self.subTest(input_text=input_text):
               result = normalize_pay_rate(input_text)
               self.assertEqual(result[0], expected)
   
   def test_hourly_ranges(self):
      """Test hourly rate ranges return tuples with midpoint and note"""
      test_cases = [
         ("$20/hr - $30/hr", "$52,000"), 
         ("$23.50 - $26.00 an hour - Full-time", "$51,480"),
         ("$20.0 - $30.0/hr", "$52,000"),
         ("$20.0/hr - $30.0/hr", "$52,000"),
         ("$20.0/hour - $30.0/hour", "$52,000"),
         ("$20 - $30 per hour", "$52,000"),
         ("$20-$30/hr", "$52,000"),
         ("$20-$30 per hour", "$52,000")
      ]
      for input_text, expected in test_cases:
         with self.subTest(input_text=input_text):
               result = normalize_pay_rate(input_text)
               self.assertEqual(result[0], expected)
   
   def test_annual_k_notation(self):
      """Test annual salaries with K notation"""
      test_cases = [
         ("$75k/yr", "$75,000"),
         ("$120K /yr", "$120,000"),
         ("$45.5k/yr", "$45,500"),
         ("$\t100k/yr", "$100,000"),
         ("$ 200 k / yr", "$200,000"),
      ]
      for input_text, expected in test_cases:
         with self.subTest(input_text=input_text):
               result = normalize_pay_rate(input_text)
               self.assertEqual(result[0], expected)
   
   def test_explicit_annual_salaries(self):
      """Test explicit annual salaries"""
      test_cases = [
         ("$75000/yr", "$75,000"),
         ("$100000 /yr", "$100,000"),
         ("$45,000/yr", "$45,000"),
         ("$123,456/yr", "$123,456"),
         ("$\t65000/yr", "$65,000"),
      ]
      for input_text, expected in test_cases:
         with self.subTest(input_text=input_text):
               result = normalize_pay_rate(input_text)
               self.assertEqual(result[0], expected)
   
   def test_annual_ranges(self):
      """Test annual salary ranges return tuples"""
      result = normalize_pay_rate("$60,000/yr - $80,000/yr")
      self.assertIsInstance(result, tuple)
      self.assertEqual(len(result), 2)
      self.assertEqual(result[0], "$70,000")  # Midpoint
      self.assertIn("Original range:", result[1])
   
   def test_typo_dollar_per_year_conversion(self):
      """Test the $X/yr typo case (likely meant $X/hr)"""
      # These should be converted from likely typos
      self.assertEqual(normalize_pay_rate("$30/yr")[0], "$62,400")
      self.assertEqual(normalize_pay_rate("$25/yr")[0], "$52,000")
      self.assertEqual(normalize_pay_rate("$15.50/yr")[0], "$32,240")
      
      # These should NOT be converted (reasonable annual salaries)
      self.assertEqual(normalize_pay_rate("$30000/yr")[0], "$30,000")
      self.assertEqual(normalize_pay_rate("$50000/yr")[0], "$50,000")
   
   def test_up_to_formats(self):
      """Test 'up to' formats"""
      self.assertEqual(normalize_pay_rate("up to $50/hr")[0], "$104,000")
      self.assertEqual(normalize_pay_rate("Up to $35.75 /hr")[0], "$74,360")
   
   def test_starting_at_formats(self):
      """Test 'starting at' formats"""
      self.assertEqual(normalize_pay_rate("starting at $75k/yr")[0], "$75,000")
      self.assertEqual(normalize_pay_rate("Starting at $60K /yr")[0], "$60,000")
   
   def test_mixed_content_with_work_keywords(self):
      """Test that mixed content with work type keywords returns '?'"""
      mixed_cases = [
         ("$50/hr - hybrid work", "$104,000"),
         ("remote - $75k/yr", "$75,000"),
         ("full-time $100,000/yr", "$100,000"),
         ("on-site position: $30/hr", "$62,400")
      ]
      for input_text, expected in mixed_cases:
         with self.subTest(input_text=input_text):
            result = normalize_pay_rate(input_text)
            self.assertEqual(result[0], expected) 
   
   def test_unusual_formatting_and_spacing(self):
      """Test handling of unusual spacing and formatting"""
      self.assertEqual(normalize_pay_rate("$  45  /  hr")[0], "$93,600")
      self.assertEqual(normalize_pay_rate("$\n60\n/\nhr")[0], "$124,800")
   
   def test_high_rate_boundaries(self):
      """Test very high rates"""
      self.assertEqual(normalize_pay_rate("$500/hr")[0], "$1,040,000")
      self.assertEqual(normalize_pay_rate("$1000/hr")[0], "$2,080,000")
   
   def test_decimal_precision(self):
      """Test decimal precision handling"""
      self.assertEqual(normalize_pay_rate("$22.75/hr")[0], "$47,320")
      self.assertEqual(normalize_pay_rate("$67.5k/yr")[0], "$67,500")
   
   def test_no_pattern_match_returns_original(self):
      """Test that unmatched but valid-looking text returns original"""
      test_cases = [
         "competitive salary",
         "doe",
         "negotiable",
         "$50,000",  # Missing /yr
         "75k",  # Missing $ and /yr
         "salary: $100,000",  # Extra text
      ]
      for case in test_cases:
         with self.subTest(case=case):
               result = normalize_pay_rate(case)
               self.assertEqual(result[0], case)
   
   def test_case_insensitivity(self):
      """Test case insensitivity"""
      self.assertEqual(normalize_pay_rate("$50/HR")[0], "$104,000")
      self.assertEqual(normalize_pay_rate("$75K/YR")[0], "$75,000")
      self.assertEqual(normalize_pay_rate("HyBrId WoRk")[0], "?")
   
   def test_special_characters_and_noise(self):
      """Test handling of special characters and noise without work keywords"""
      result = normalize_pay_rate("Salary: $50/hr (negotiable)")
      self.assertEqual(result[0], "$104,000")
   
   def test_low_rate_boundaries(self):
      """Test very low hourly rates"""
      self.assertEqual(normalize_pay_rate("$0.01/hr")[0], "$21")
      self.assertEqual(normalize_pay_rate("$1/hr")[0], "$2,080")
   
   def test_various_whitespace_scenarios(self):
      """Test various whitespace scenarios"""
      test_cases = [
         ("$50/hr", "$104,000"),
         ("$50 /hr", "$104,000"),
         ("$50/ hr", "$104,000"),
         ("$50 / hr", "$104,000"),
         ("$\t50\t/\thr", "$104,000"),
      ]
      for input_text, expected in test_cases:
         with self.subTest(input_text=input_text):
               result = normalize_pay_rate(input_text)
               self.assertEqual(result[0], expected)
   
   def test_range_parsing_edge_cases(self):
      """Test range parsing edge cases"""
      # Three numbers in text (should only use first two)
      result = normalize_pay_rate("$20/hr $30/hr $40/hr")
      self.assertIsInstance(result, tuple)
      self.assertEqual(len(result), 2)
      
      # Inverted range (should still work)
      result = normalize_pay_rate("$30/hr - $20/hr")
      self.assertIsInstance(result, tuple)
      self.assertEqual(len(result), 2)
   
   def test_numeric_formats_with_commas(self):
      """Test various numeric formats with commas"""
      self.assertEqual(normalize_pay_rate("$1,000/hr")[0], "$2,080,000")
      self.assertEqual(normalize_pay_rate("$75,000/yr")[0], "$75,000")
      self.assertEqual(normalize_pay_rate("$100000/yr")[0], "$100,000")
   
   def test_multiple_linkedin_domains_preserved(self):
      """Test that different URLs with same domain are preserved"""
      # This test is inspired by your original test structure
      linkedin_urls = [
         "https://www.linkedin.com/jobs/view/123",
         "https://linkedin.com/jobs/view/456"
      ]
      # These should return as-is since they don't match pay rate patterns
      for url in linkedin_urls:
         with self.subTest(url=url):
               result = normalize_pay_rate(url)
               self.assertEqual(result[0], url)
   
   def test_duplicate_removal_not_applicable(self):
      """Test that function doesn't remove duplicates (unlike your original test)"""
      # This function doesn't handle duplicates, so test that same input gives same output
      result1 = normalize_pay_rate("$50/hr")
      result2 = normalize_pay_rate("$50/hr")
      self.assertEqual(result1[0], result2[0])
      self.assertEqual(result1[0], "$104,000")
   
   def test_empty_string_handling(self):
      """Test empty string handling"""
      result = normalize_pay_rate("")
      self.assertEqual(result[0], "?")
   
   def test_malformed_url_handling(self):
      """Test malformed URL handling (should return as-is)"""
      malformed = "invalid-url"
      result = normalize_pay_rate(malformed)
      self.assertEqual(result[0], malformed)
   
   def test_common_cases_parameterized(self):
      """Parameterized tests for common cases"""
      test_cases = [
         ("$50/hr", "$104,000"),
         ("$75k/yr", "$75,000"),
         ("hybrid", "?"),
         ("?", "?"),
         ("$60000/yr", "$60,000"),
         ("$30/yr", "$62,400"),  # Typo case
         ("$30000/yr", "$30,000"),  # Not a typo
      ]
      
      for input_text, expected in test_cases:
         with self.subTest(input_text=input_text, expected=expected):
               result = normalize_pay_rate(input_text)
               self.assertEqual(result[0], expected)
   
   def test_range_cases_parameterized(self):
      """Parameterized tests for range cases"""
      test_cases = [
         ("$25/hr - $35/hr", "$62,400"),  # Midpoint
         ("$60,000/yr - $80,000/yr", "$70,000"),  # Midpoint
         ("$77.2K/yr - $115.8K/yr", "$96,500"),  # Midpoint
         ("$45,600 - $80,000", "$62,800") # Midpoint
      ]
      
      for input_text, expected_midpoint in test_cases:
         with self.subTest(input_text=input_text, expected_midpoint=expected_midpoint):
               result = normalize_pay_rate(input_text)
               self.assertIsInstance(result, tuple)
               self.assertEqual(result[0], expected_midpoint)

class TestPreProcessJobLinks(unittest.TestCase):
   
   def setUp(self):
      """Set up test CSV files before each test"""
      self.temp_dir = tempfile.mkdtemp()
      
      # Test data for various scenarios
      self.linkedin_links = [
         'https://www.linkedin.com/jobs/view/123456789/',
         'https://linkedin.com/jobs/view/987654321/extra/path',
         'https://www.linkedin.com/jobs/view/555555555/?some=param',
      ]
      
      self.indeed_links = [
         'https://www.indeed.com/viewjob?jk=abc123def',
         'https://indeed.com/viewjob?jk=xyz789uvw&extra=param',
         'https://www.indeed.com/viewjob?jk=lmn456opq/extra/path',
      ]
      
      self.mixed_domain_links = [
         'https://apple.com/jobs/123',
         'https://beta.company.com/jobs/456',
         'https://alpha.org/careers/789',
         'https://google.com/positions/101',
         'https://microsoft.com/careers/112'
      ]
      
      self.duplicate_links = [
         'https://zebra.com/jobs/1',
         'https://yahoo.com/careers/2',
         'https://xerox.com/positions/3',
         'https://yahoo.com/careers/2',  # duplicate
         'https://uber.com/jobs/4'
      ]
      
      self.edge_case_links = [
         'https://www.linkedin.com/jobs/view/123',  # with www
         'https://linkedin.com/jobs/view/456',      # without www
         'invalid-url',                             # malformed URL
         '',                                        # empty string
         'https://indeed.com/viewjob?jk=789',
         'http://mixed-protocol.org/jobs/101',      # http instead of https
         'https://www.indeed.com/viewjob?jk=987'    # another with www
      ]
      
      # Create test CSV files
      self.test_csv_linkedin = self._create_test_csv('test_linkedin.csv', self.linkedin_links)
      self.test_csv_indeed = self._create_test_csv('test_indeed.csv', self.indeed_links)
      self.test_csv_mixed = self._create_test_csv('test_mixed.csv', self.mixed_domain_links)
      self.test_csv_duplicates = self._create_test_csv('test_duplicates.csv', self.duplicate_links)
      self.test_csv_edge = self._create_test_csv('test_edge.csv', self.edge_case_links)
      self.test_csv_empty = self._create_test_csv('test_empty.csv', [])
   
   def tearDown(self):
      """Clean up test files after each test"""
      for file_path in [
         self.test_csv_linkedin, self.test_csv_indeed, self.test_csv_mixed,
         self.test_csv_duplicates, self.test_csv_edge, self.test_csv_empty
      ]:
         if os.path.exists(file_path):
               os.remove(file_path)
      if os.path.exists(self.temp_dir):
         os.rmdir(self.temp_dir)
   
   def _create_test_csv(self, file_name, links):
      """Helper method to create test CSV files"""
      file_path = os.path.join(self.temp_dir, file_name)
      with open(file_path, 'w', newline='', encoding='utf-8') as file:
         writer = csv.writer(file)
         for link in links:
               writer.writerow([link])
      return file_path

   @patch('main.type_text')
   def test_pre_process_links_az_sorting(self, mock_type_text):
      """Test sorting links by domain in A-Z order"""
      result = pre_process_job_links(self.test_csv_mixed, ascending_alphabetically=True)
      
      # Extract domains for verification
      domains = []
      for url in result:
         try:
               parsed = urlparse(url)
               domain = parsed.netloc.lower()
               if domain.startswith('www.'):
                  domain = domain[4:]
               domains.append(domain)
         except:
               domains.append('')
      
      # Check if domains are sorted A-Z
      expected_domains = sorted(domains)
      self.assertEqual(domains, expected_domains, "Domains should be sorted A-Z")

   @patch('main.type_text')
   def test_pre_process_links_za_sorting(self, mock_type_text):
      """Test sorting links by domain in Z-A order"""
      result = pre_process_job_links(self.test_csv_mixed, ascending_alphabetically=False)
      
      # Extract domains for verification
      domains = []
      for url in result:
         try:
               parsed = urlparse(url)
               domain = parsed.netloc.lower()
               if domain.startswith('www.'):
                  domain = domain[4:]
               domains.append(domain)
         except:
               domains.append('')
      
      # Check if domains are sorted Z-A
      expected_domains = sorted(domains, reverse=True)
      self.assertEqual(domains, expected_domains, "Domains should be sorted Z-A")

   @patch('main.type_text')
   def test_pre_process_linkedin_normalization(self, mock_type_text):
      """Test LinkedIn URL normalization"""
      result = pre_process_job_links(self.test_csv_linkedin, ascending_alphabetically=True)
      
      # Check that LinkedIn URLs are properly normalized
      for url in result:
         if 'linkedin.com' in url:
               # Should not have parameters or extra path after the job ID
               self.assertNotIn('?', url, "LinkedIn URLs should not have query parameters")
               # Should end with slash after job ID
               self.assertTrue(url.endswith('/'), "Normalized LinkedIn URLs should end with slash")

   @patch('main.type_text')
   def test_pre_process_indeed_normalization(self, mock_type_text):
      """Test Indeed URL normalization"""
      result = pre_process_job_links(self.test_csv_indeed, ascending_alphabetically=True)
      
      # Check that Indeed URLs are properly normalized
      for url in result:
         if 'indeed.com' in url:
               # Should not have extra parameters after job key
               self.assertNotIn('&', url, "Indeed URLs should not have extra parameters")
               self.assertNotIn('?extra=', url, "Indeed URLs should not have extra query params")

   @patch('main.type_text')
   def test_pre_process_duplicate_removal(self, mock_type_text):
      """Test that duplicates are removed during processing"""
      result = pre_process_job_links(self.test_csv_duplicates, ascending_alphabetically=True)
      
      # Check that duplicates are removed
      self.assertEqual(len(result), 4, "Duplicates should be removed")
      
      # Count occurrences of each unique URL
      url_counts = {}
      for url in result:
         url_counts[url] = url_counts.get(url, 0) + 1
      
      # All URLs should appear only once
      for url, count in url_counts.items():
         self.assertEqual(count, 1, f"URL {url} should appear only once")

   @patch('main.type_text')
   def test_pre_process_empty_file(self, mock_type_text):
      """Test processing with an empty CSV file"""
      result = pre_process_job_links(self.test_csv_empty, ascending_alphabetically=True)
      self.assertEqual(result, [], "Empty file should return empty list")

   @patch('main.type_text')
   def test_pre_process_edge_cases(self, mock_type_text):
      """Test processing with edge cases including malformed URLs"""
      result = pre_process_job_links(self.test_csv_edge, ascending_alphabetically=True)
      
      # Should handle various edge cases
      self.assertIn('invalid-url', result, "Should handle malformed URLs")
      
      # Empty strings should be filtered out by read_job_links
      self.assertNotIn('', result, "Empty strings should be filtered out")
   
   @patch('main.type_text')
   def test_pre_process_domain_consistency(self, mock_type_text):
      """Test that www and non-www domains are treated consistently"""
      result = pre_process_job_links(self.test_csv_edge, ascending_alphabetically=True)
      
      linkedin_domains = []
      indeed_domains = []
      
      for url in result:
         if 'linkedin' in url:
               parsed = urlparse(url)
               domain = parsed.netloc.lower()
               if domain.startswith('www.'):
                  domain = domain[4:]
               linkedin_domains.append(domain)
         elif 'indeed' in url:
               parsed = urlparse(url)
               domain = parsed.netloc.lower()
               if domain.startswith('www.'):
                  domain = domain[4:]
               indeed_domains.append(domain)
      
      # All LinkedIn domains should be normalized to same base
      unique_linkedin_domains = set(linkedin_domains)
      self.assertEqual(len(unique_linkedin_domains), 1, "All LinkedIn domains should normalize to same base")
      
      # All Indeed domains should be normalized to same base
      unique_indeed_domains = set(indeed_domains)
      self.assertEqual(len(unique_indeed_domains), 1, "All Indeed domains should normalize to same base")
   
   @patch('main.type_text')
   def test_pre_process_preserves_non_linkedin_indeed_links(self, mock_type_text):
      """Test that non-LinkedIn/Indeed links are preserved as-is"""
      result = pre_process_job_links(self.test_csv_mixed, ascending_alphabetically=True)
      
      # Check that non-LinkedIn/Indeed links are preserved
      for url in result:
         if 'linkedin.com' not in url and 'indeed.com' not in url:
               # These should be in the original mixed_domain_links
               self.assertIn(url, self.mixed_domain_links, "Non-LinkedIn/Indeed links should be preserved")
   
   @patch('main.type_text')
   def test_pre_process_order_preservation_within_domains(self, mock_type_text):
      """Test that order is preserved for links within the same domain"""
      # Create test data with multiple links from same domain
      same_domain_links = [
         'https://example.com/job1',
         'https://example.com/job3',
         'https://example.com/job2',
         'https://test.com/jobA',
         'https://test.com/jobC',
         'https://test.com/jobB'
      ]
      
      test_csv = self._create_test_csv('test_same_domain.csv', same_domain_links)
      
      try:
         result = pre_process_job_links(test_csv, ascending_alphabetically=True)
         
         # Extract example.com links in result order
         example_links = [url for url in result if 'example.com' in url]
         test_links = [url for url in result if 'test.com' in url]
         
         # Order within same domain should be preserved as per original CSV order
         self.assertEqual(example_links, ['https://example.com/job1', 'https://example.com/job3', 'https://example.com/job2'],
                        "Order within same domain should be preserved")
         self.assertEqual(test_links, ['https://test.com/jobA', 'https://test.com/jobC', 'https://test.com/jobB'],
                        "Order within same domain should be preserved")
      
      finally:
         if os.path.exists(test_csv):
               os.remove(test_csv)
   
   @patch('main.type_text')
   def test_pre_process_comprehensive_workflow(self, mock_type_text):
      """Test the complete preprocessing workflow with all operations"""
      # Create comprehensive test data
      comprehensive_links = [
         'https://www.linkedin.com/jobs/view/123456789/?some=param',
         'https://zebra.com/jobs/1',
         'https://indeed.com/viewjob?jk=abc123&extra=stuff',
         'https://apple.com/jobs/123',
         'https://www.linkedin.com/jobs/view/987654321/extra/path',
         'https://zebra.com/jobs/1',  # duplicate
         'https://alpha.org/careers/789',
      ]
      
      test_csv = self._create_test_csv('test_comprehensive.csv', comprehensive_links)
      
      try:
         result = pre_process_job_links(test_csv, ascending_alphabetically=True)
         
         # Verify no duplicates
         self.assertEqual(len(result), len(set(result)), "No duplicates should exist")
         
         # Verify sorting order (A-Z)
         domains = []
         for url in result:
               parsed = urlparse(url)
               domain = parsed.netloc.lower()
               if domain.startswith('www.'):
                  domain = domain[4:]
               domains.append(domain)
         
         self.assertEqual(domains, sorted(domains), "Domains should be sorted A-Z")
         
         # Verify LinkedIn normalization
         linkedin_urls = [url for url in result if 'linkedin.com' in url]
         for url in linkedin_urls:
               self.assertNotIn('?', url, "LinkedIn URLs should be normalized")
         
         # Verify Indeed normalization  
         indeed_urls = [url for url in result if 'indeed.com' in url]
         for url in indeed_urls:
               self.assertNotIn('&extra=', url, "Indeed URLs should be normalized")
      
      finally:
         if os.path.exists(test_csv):
               os.remove(test_csv)
   
   @patch('main.type_text')
   def test_pre_process_linkedin_tracking_parameter_normalization(self, mock_type_text):
      """Test that LinkedIn URLs with different tracking parameters get normalized to the same unique link"""
      # These are the same job listing but with different tracking parameters
      linkedin_duplicates = [
         'https://www.linkedin.com/jobs/view/4323925341/?eBP=CwEAAAGaMraZrD-W9mhaOKa7yye6_iZ31epl1KRLpa5dFHuHQxQ9Rnx8-Wcla31rr3eTcX3qiWhVDnV2_OpYkJh1F3ZMeFlYzfiJoCLKeljPudFWFYnb3_VWAZVp-L9AyEkX6766ezKU47e4SpmdRMn0PLXGx4W8u2FUfxW4zx-Izetl0v1CXx8RghLpc8d56UkQvrrVUpgrOKilAXUrjqKTPK5xHqENRLP9bzGYtKFTy5Edei7K0mTr1HFLPthbkm_uArrTedIROycvCjB0kOGR9JPUSp5LRnMidWkKmhdNxJIKlnpY-D3er2AYv7XGqnZaPnpuswOJ-ObwvZjuOXk8asyDRUy5AvmTBh5GBxJDzsbHToscA4VYuOl6bOACq0XOdiFAuMBDAuBKiyLigfQ6pvxJGosXI1b7GSXittUF6gx7S1bFMegRN0v7SotMC1iobfoimEl5e3wJbObIOE51asBNs7bn04FbN3A89d7Zb-lKn_bktXGoYELmP36GdZu4QF6kvDBwnELZ&refId=nNlHFGDJWHiv7TdxNcZzBQ%3D%3D&trackingId=t6TUf%2FvqPhGaYfPQx1hyNQ%3D%3D&trk=flagship3_search_srp_jobs&lipi=urn%3Ali%3Apage%3Ad_flagship3_search_srp_jobs%3BLdRWkXV3QTORcrq1uX8rPA%3D%3D&lici=t6TUf%2FvqPhGaYfPQx1hyNQ%3D%3D',
         'https://www.linkedin.com/jobs/view/4323925341/?eBP=CwEAAAGaMrhAFRlSXySymqwHExFwiu5aDfVEIeMLQ-GZaHB4N5jwjHU4tv4ruh6oO-umTJFProZl9dwZ4ilJiQ7rjPgQkwIXsERkKW8hKT-xZE0M42LU6pcCC6tWbnHQXHQ_pRFyvWdG3kredRVXiUnKT7NG8dbJO8GyR60kw0b7XDghZoG4afCzANnuL-XDYKvRvJD53s7OEhlo8NWhislgV0CVYO9ddZVwNSknP3G9j_dkXhvQrlA4rhBbV3_gaxByOf4EgJgH2ilENz-Gkmf6d7XBGH7ZOnLTFmtenRF7DLLTuyARhua6V17PQ49voqbzflzESuDACsNDhzkilHot8RQx3td81xEyyRIu6tejRScf9VpD2Vs0tiOxHQU_2huifZuUX2sNaTGt2Ug6n1Z0qlPKx5mnUvpsd9MelO2AsCc8KdEKNnT2fEAyu174IdxDyrRBhK6nnM-L6mhO1I9DqmA2p_OS-ncAsJwDfG9k0JcI5rpQ9PAYYCu9bmyV1UCrtpjyfkWcc_kE4c0&refId=sn1iyIDNubaV%2Brb6siKpbg%3D%3D&trackingId=ki5zKAQKWYRh2wmStXWY7w%3D%3D&trk=flagship3_search_srp_jobs&lipi=urn%3Ali%3Apage%3Ad_flagship3_search_srp_jobs%3BLdRWkXV3QTORcrq1uX8rPA%3D%3D&lici=ki5zKAQKWYRh2wmStXWY7w%3D%3D'
      ]
      
      test_csv = self._create_test_csv('test_linkedin_tracking.csv', linkedin_duplicates)
      
      try:
         result = pre_process_job_links(test_csv, ascending_alphabetically=True)
         
         # Debug output to see what we got
         # print(f"DEBUG: Input had {len(linkedin_duplicates)} LinkedIn URLs with tracking")
         # print(f"DEBUG: Output has {len(result)} URLs after processing")
         for i, url in enumerate(result):
               print(f"DEBUG: Result {i}: {url}")
         
         # The two URLs should normalize to the SAME URL and duplicates should be removed
         # So we should only have 1 unique LinkedIn URL in the result
         self.assertEqual(len(result), 1, "Two LinkedIn URLs with same job ID but different tracking should normalize to one unique link")
         
         # The normalized URL should be the base LinkedIn URL without tracking parameters
         normalized_url = result[0]
         self.assertIn('linkedin.com', normalized_url)
         self.assertIn('/4323925341/', normalized_url)  # Should contain the job ID
         self.assertNotIn('?', normalized_url, "Normalized LinkedIn URL should not have query parameters")
         self.assertTrue(normalized_url.endswith('/'), "Normalized LinkedIn URL should end with slash")
         
         # Verify the exact expected format
         expected_url = 'https://www.linkedin.com/jobs/view/4323925341/'
         self.assertEqual(normalized_url, expected_url, f"Normalized URL should be {expected_url}")
      
      finally:
         if os.path.exists(test_csv):
               os.remove(test_csv)



if __name__ == '__main__':
   import time
   
   # Run tests and capture results
   start_time = time.time()
   result = unittest.main(verbosity=2, exit=False)
   end_time = time.time()
   
   # Extract results
   total_tests = result.result.testsRun
   failures = len(result.result.failures)
   errors = len(result.result.errors)
   passed = total_tests - failures - errors
   pass_rate = (passed / total_tests) * 100
   duration = end_time - start_time
   
   # Print summary
   print("")
   type_text("="*56)
   print_applybot_mascot_w_statistics()
   type_text(f"\n🧪 TESTS COMPLETE: {passed}/{total_tests} passed ({pass_rate:.1f}%)")
   type_text(f"⏱️  Duration: {duration:.3f}s")
   type_text("="*56)
   
   # Exit with appropriate code
   sys.exit(1 if (failures > 0 or errors > 0) else 0)
