import unittest
import os
import csv
from urllib.parse import urlparse

# Import the functions from your main module
# Assuming they are in a file called job_preparation.py
from main import sort_job_links_by_domain, read_job_links, remove_duplicate_links

class TestJobListingPreparation(unittest.TestCase):
   def setUp(self):
      """Set up test CSV files before each test"""
      self.test_csv_az = 'test_links_az.csv'
      self.test_csv_za = 'test_links_za.csv'
      self.test_csv_edge = 'test_links_edge.csv'
      self.test_csv_empty = 'test_links_empty.csv'
      
      # Test data for A-Z sorting
      az_links = [
         'https://apple.com/jobs/123',
         'https://beta.company.com/jobs/456',
         'https://alpha.org/careers/789',
         'https://google.com/positions/101',
         'https://microsoft.com/careers/112'
      ]
      
      # Test data for Z-A sorting (includes duplicates)
      za_links = [
         'https://zebra.com/jobs/1',
         'https://yahoo.com/careers/2',
         'https://xerox.com/positions/3',
         'https://yahoo.com/careers/2',  # duplicate
         'https://uber.com/jobs/4'
      ]
      
      # Test data for edge cases
      edge_links = [
         'https://www.linkedin.com/jobs/view/123',  # with www
         'https://linkedin.com/jobs/view/456',      # without www
         'invalid-url',                             # malformed URL
         '',                                        # empty string
         'https://indeed.com/job/789',
         'http://mixed-protocol.org/jobs/101',      # http instead of https
         'https://www.indeed.com/job/987'           # another with www
      ]
      
      # Create test CSV files
      self._create_test_csv(self.test_csv_az, az_links)
      self._create_test_csv(self.test_csv_za, za_links)
      self._create_test_csv(self.test_csv_edge, edge_links)
      self._create_test_csv(self.test_csv_empty, [])
   
   def tearDown(self):
      """Clean up test files after each test"""
      for file_path in [self.test_csv_az, self.test_csv_za, self.test_csv_edge, self.test_csv_empty]:
         if os.path.exists(file_path):
               os.remove(file_path)
   
   def _create_test_csv(self, file_path, links):
      """Helper method to create test CSV files"""
      with open(file_path, 'w', newline='', encoding='utf-8') as file:
         writer = csv.writer(file)
         for link in links:
               writer.writerow([link])
   
   def test_sort_az_alphabetically(self):
      """Test sorting links by domain in A-Z order"""
      result = sort_job_links_by_domain(self.test_csv_az, ascending_alphabetically=True)
      
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
      
      # Verify specific order
      expected_order = [
         'https://alpha.org/careers/789',
         'https://apple.com/jobs/123',
         'https://beta.company.com/jobs/456',
         'https://google.com/positions/101',
         'https://microsoft.com/careers/112'
      ]
      self.assertEqual(result, expected_order, "Links should be sorted by domain A-Z")
   
   def test_sort_za_alphabetically(self):
      """Test sorting links by domain in Z-A order"""
      result = sort_job_links_by_domain(self.test_csv_za, ascending_alphabetically=False)
      
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
      
      # Verify specific order and duplicate removal
      expected_order = [
         'https://zebra.com/jobs/1',
         'https://yahoo.com/careers/2',  # duplicate should be removed
         'https://xerox.com/positions/3',
         'https://uber.com/jobs/4'
      ]
      self.assertEqual(result, expected_order, "Links should be sorted by domain Z-A and duplicates removed")
   
   def test_edge_cases(self):
      """Test sorting with edge cases including malformed URLs, empty strings, and www prefixes"""
      result = sort_job_links_by_domain(self.test_csv_edge, ascending_alphabetically=True)
      
      # The function should handle:
      # - URLs with www prefix (should be normalized)
      # - Malformed URLs
      # - Empty strings
      # - Duplicate domains with different protocols or www prefixes
      
      # Verify that www domains are normalized (linkedin.com and www.linkedin.com should be treated the same)
      linkedin_count = 0
      indeed_count = 0
      
      for url in result:
         if 'linkedin' in url:
               linkedin_count += 1
         if 'indeed' in url:
               indeed_count += 1
      
      # Should have both linkedin URLs (they are different URLs even if same domain)
      self.assertEqual(linkedin_count, 2, "Should preserve both linkedin URLs")
      self.assertEqual(indeed_count, 2, "Should preserve both indeed URLs")
      
      # Verify malformed URL and empty string are handled
      self.assertIn('invalid-url', result, "Should handle malformed URLs")
      
      # Check that empty strings are filtered out (based on read_job_links behavior)
      self.assertNotIn('', result, "Empty strings should be filtered out")
   
   def test_empty_file(self):
      """Test sorting with an empty CSV file"""
      result = sort_job_links_by_domain(self.test_csv_empty, ascending_alphabetically=True)
      self.assertEqual(result, [], "Empty file should return empty list")
   
   def test_duplicate_removal(self):
      """Test that duplicates are removed before sorting"""
      # Create a CSV with duplicates
      duplicate_links = [
         'https://example.com/job1',
         'https://test.com/job2',
         'https://example.com/job1',  # duplicate
         'https://alpha.com/job3'
      ]
      
      self._create_test_csv('test_duplicates.csv', duplicate_links)
      
      result_az = sort_job_links_by_domain('test_duplicates.csv', ascending_alphabetically=True)
      
      # Check that duplicates are removed
      self.assertEqual(len(result_az), 3, "Duplicates should be removed")
      self.assertEqual(result_az.count('https://example.com/job1'), 1, "Should have only one instance of duplicate")
      
      # Clean up
      if os.path.exists('test_duplicates.csv'):
         os.remove('test_duplicates.csv')

if __name__ == '__main__':
   # Run the tests
   unittest.main(verbosity=2)