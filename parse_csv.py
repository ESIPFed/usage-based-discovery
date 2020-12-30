#!/usr/bin/env python

import sys
import csv
import platform
from csv import reader, writer

import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
import re
import urllib.request
from urllib.request import urlopen

from time import sleep

import nltk
from nltk.tokenize import sent_tokenize

import argparse
def parse_options():
    parser = argparse.ArgumentParser(description="Parse CSV for input into UBD Neptune database")
    # TODO: default to stdin and stdout
    parser.add_argument('-i', '--ifile', default='algo-input.csv',
        metavar="input-pathname")
    parser.add_argument('-o', '--ofile', default='algo-output.csv',
        metavar="output-pathname")
    return(parser.parse_args())



def get_chrome_driver():
    """figure out which chromedriver to use from 
    https://chromedriver.storage.googleapis.com/:
    linux64 or mac64
    """
    os_suffix = {'Linux':'linux64', 'darwin':'mac64'}

    path = "./chromedriver87." + os_suffix.get(platform.system())
    # initiate selenium webdriver
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    return webdriver.Chrome(path, options=option)

# this function generates the snapshot for the specified application url
# and saves it to the static folder in the project directory
def get_snapshot(driver, url, count):

    name = "app" + str(count) + ".png"
    
    driver.get(url)
    sleep(2)
    driver.get_screenshot_as_file('static/' + name)

    return name

# Main program
args = parse_options()
chrome_driver = get_chrome_driver()
# opening the CSV file
with open(args.ifile, 'r') as input, \
    open(args.ofile, 'w') as output:

    # specifies header columns of output csv file
    fieldnames=['topic','name','site', 'screenshot', 'description', \
        'publication', 'query', 'doi','title']

    # initiate csv reader and writer
    reader = csv.DictReader(input)
    writer = csv.DictWriter(output, fieldnames=fieldnames)

    writer.writeheader()

    count = 1

    # keeps track of which apps have already been seen
    apps = set()
    
    for line in reader: 

        # automated generation of dataset name from the doi
        '''
        # GET DATASET NAME, application dataset matching algorithm takes care of this
        doi = line['doi']
        doi = doi.split("g/")[1]
        url = "https://api.datacite.org/dois/" + doi
        headers = {"Accept": "application/vnd.api+json"}
        response = requests.request("GET", url, headers=headers)
        title = response.json()['data']['attributes']['titles'][0]
        print(title['title'])
        line['title'] = title['title']
        '''
       
        # automated generation of application screenshot from website link

        # this conditional handles duplicate application values
        if line['name'] not in apps:
            line['screenshot'] = get_snapshot(chrome_driver, line['site'], count)
            count += 1
        
        # semi-automated generation application website description 
        # needs refinement, could be explored with nlp applications due to 
        # the large amount of edge cases
        '''
        # GET APP DESCRIPTION, semi-automated for now due to edge cases
        req = requests.get(line['site'])
        soup = BeautifulSoup(req.text, 'html5lib')
        topics = ['map', 'model', 'product', 'NASA', 'flood', 'fire', 'landslide'] # and more
        for p in soup.find_all('p'):
            for topic in topics:
                if topic in p.get_text():
                    sentence = sent_tokenize(p.get_text())
                    
        # line['description'] = sentence[0]
        '''

        # add app to set to indicate it has already been seen
        apps.add(line['name'])
        
        
        writer.writerow(line)

