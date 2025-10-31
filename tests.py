import unittest
import os
import csv
import pandas as pd
import re
import sys
from urllib.parse import urlparse
from main import normalize_pay_rate, type_text, print_applybot_mascot_w_statistics

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
      result = normalize_pay_rate("$20/hr - $30/hr")
      self.assertIsInstance(result, tuple)
      self.assertEqual(len(result), 2)
      self.assertEqual(result[0], "$52,000")  # Midpoint of $41,600 and $62,400
      self.assertIn("Original range:", result[1])
   
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
         "$50/hr - hybrid work",
         "remote - $75k/yr",
         "full-time $100,000/yr",
         "on-site position: $30/hr"
      ]
      for case in mixed_cases:
         with self.subTest(case=case):
               result = normalize_pay_rate(case)
               self.assertEqual(result[0], "?")
   
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


class TestNormalizePayRateParameterized(unittest.TestCase):
   """Parameterized test cases using subTest"""
   
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
      ]
      
      for input_text, expected_midpoint in test_cases:
         with self.subTest(input_text=input_text, expected_midpoint=expected_midpoint):
               result = normalize_pay_rate(input_text)
               self.assertIsInstance(result, tuple)
               self.assertEqual(result[0], expected_midpoint)


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
