#!/usr/bin/env python
""" parse_csv.py parses an input CSV file with Application - Dataset relationships
(plus several key properties, like URL), obtains a screenshot of the application's
front page, and outputs a CSV file that is suitable for load_graph.py to load into
the graph database.
"""
import sys
import csv
import platform
import re
# import urllib.request
# from urllib.request import urlopen
from time import sleep
import argparse

# import requests

from selenium import webdriver
# from selenium.webdriver.chrome.options import Options

def parse_options():
    """ Parse the command line options for input and output files """
    parser = argparse.ArgumentParser(description="Parse CSV for input into UBD Neptune database")
    parser.add_argument('-i', '--ifile', default='algo-input.csv',
                        metavar="input-pathname")
    parser.add_argument('-o', '--ofile', default='algo-output.csv',
                        metavar="output-pathname")
    return parser.parse_args()


def get_chrome_driver():
    """figure out which chromedriver to use from
    https://chromedriver.storage.googleapis.com/:
    linux64 or mac64
    """
    os_suffix = {'Linux':'linux64', 'Darwin':'mac64'}

    path = "./chromedriver87." + os_suffix.get(platform.system())
    # initiate selenium webdriver
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    return webdriver.Chrome(path, options=option)

# this function generates the snapshot for the specified application url
# and saves it to the static folder in the project directory
def get_snapshot(driver, url):
    """
    Fetch a snapshot of the application home page using Selenium

    Positional Arguments
    driver:  selenium driver
    url:  application URL

    Returns output filename, basically the meat of the URL,
    using '-' in place of non-alphnumeric chars, plus .png
    """

    filename = re.sub(r'^https?://', '', url)
    filename = re.sub(r'\W', '-', filename)

    driver.get(url)
    sleep(2)
    driver.get_screenshot_as_file('static/' + filename + '.png')

    return filename

# Main program
OPTIONS = parse_options()
CHROME_DRIVER = get_chrome_driver()
# opening the CSV file
with open(OPTIONS.ifile, 'r') as csv_in, \
    open(OPTIONS.ofile, 'w') as csv_out:

    # specifies header columns of output csv file
    FIELDNAMES = ['topic', 'name', 'site', 'screenshot', 'description', \
        'publication', 'query', 'doi', 'title']

    # initiate csv reader and writer
    READER = csv.DictReader(csv_in)
    WRITER = csv.DictWriter(csv_out, fieldnames=FIELDNAMES)

    WRITER.writeheader()

    # keeps track of which apps have already been seen
    apps = set()

    for line in READER:

        # automated generation of dataset name from the doi
        # GET DATASET NAME, application dataset matching algorithm takes care of this
        # doi = line['doi']
        # doi = doi.split("g/")[1]
        # url = "https://api.datacite.org/dois/" + doi
        # headers = {"Accept": "application/vnd.api+json"}
        # response = requests.request("GET", url, headers=headers)
        # title = response.json()['data']['attributes']['titles'][0]
        # print(title['title'])
        # line['title'] = title['title']

        # automated generation of application screenshot from website link
        # this conditional handles duplicate application values
        if line['name'] not in apps:
            print(f"Getting snapshot for {line['site']}", file=sys.stderr)
            line['screenshot'] = get_snapshot(CHROME_DRIVER, line['site'])

        # TODO #############################
        # semi-automated generation application website description
        # needs refinement, could be explored with nlp applications due to
        # the large amount of edge cases
        # GET APP DESCRIPTION, semi-automated for now due to edge cases
        # req = requests.get(line['site'])
        # soup = BeautifulSoup(req.text, 'html5lib')
        # topics = ['map', 'model', 'product', 'NASA', 'flood', 'fire', 'landslide'] # and more
        # for p in soup.find_all('p'):
        #   for topic in topics:
        #       if topic in p.get_text():
        #           sentence = sent_tokenize(p.get_text())
        # line['description'] = sentence[0]
        ###################################

        # add app to set to indicate it has already been seen
        apps.add(line['name'])

        WRITER.writerow(line)
