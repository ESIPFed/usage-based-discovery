#!/usr/bin/env python
""" parse_csv.py parses an input CSV file with Application - Dataset relationships
(plus several key properties, like URL), obtains a screenshot of the application's
front page, and outputs a CSV file that is suitable for load_graph.py to load into
the graph database.
"""
# parse_csv.py

import sys
import io
import csv
import platform
import re
# import urllib.request
# from urllib.request import urlopen
from time import sleep
import argparse
from s3_functions import s3Functions
# import requests

# from selenium.webdriver.chrome.options import Options

def parse_options():
    """ Parse the command line options for input and output files """
    parser = argparse.ArgumentParser(description="Parse CSV for input into UBD Neptune database")
    parser.add_argument('-i', '--ifile', default='algo-input.csv',
                        metavar="input-pathname")
    parser.add_argument('-o', '--ofile', default='algo-output.csv',
                        metavar="output-pathname")
    return parser.parse_args()

def main():
    # Main program
    OPTIONS = parse_options()
    print(OPTIONS)

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
        s3F= s3Functions()
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

            #removes spaces before and after each data point
            for i in line:
                line[i]= line[i].strip()
            #following line is obsolete after url-encoding 
            #line['name'] = line['name'].replace('/', '~slash').replace('|','~pipe')
            
            # automated generation of application screenshot from website link
            # this conditional handles duplicate application values
            if line['name'] not in apps:
                print(f"Getting snapshot for {line['site']}", file=sys.stderr)
                try:
                    line['screenshot'] = s3F.upload_image_from_url('test-bucket-parth',line['site'])
                    print("\n\n")
                except:
                    print("ERROR getting {}".format(line['site']))
                    continue
            # add app to set to indicate it has already been seen
            apps.add(line['name'])

            WRITER.writerow(line)

if __name__ == '__main__':
    main()
