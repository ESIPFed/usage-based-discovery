import unittest
import sys
from argparse import Namespace
sys.path.append("../")
from util import parse_csv

class TestParseCSVMethods(unittest.TestCase):

	def test_parse_options(self):
		expected = Namespace(ifile='algo-input.csv', ofile='algo-output.csv')
		self.assertEqual(parse_csv.parse_options(),expected)
	
	def test_get_chrome_driver(self):
		if parse_csv.get_chrome_driver():
			pass
	
	def test_get_snapshot(self):
		driver = parse_csv.get_chrome_driver()
		url = "https://www.nasa.gov/"
		expected = "www-nasa-gov-.png"
		self.assertEqual(parse_csv.get_snapshot(driver, url), expected)

if __name__=='__main__':
	unittest.main()
