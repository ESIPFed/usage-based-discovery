import pytest
import sys
from argparse import Namespace
sys.path.append("../")
from util import parse_csv

def test_parse_optionsself():
	expected = Namespace(ifile='algo-input.csv', ofile='algo-output.csv')
	assert parse_csv.parse_options() == expected

def test_get_chrome_driver():
	if parse_csv.get_chrome_driver():
		pass

def test_get_snapshot():
	driver = parse_csv.get_chrome_driver()
	url = "https://www.nasa.gov/"
	expected = "www-nasa-gov-.png"
	assert parse_csv.get_snapshot(driver, url) == expected

