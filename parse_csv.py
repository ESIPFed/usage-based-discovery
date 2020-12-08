import csv
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


option = webdriver.ChromeOptions()
option.add_argument('headless')
driver = webdriver.Chrome('./chromedriver87', options=option)


def get_snapshot(url, count):

    name = "app" + str(count) + ".png"
    
    driver.get(url)
    sleep(1)
    driver.get_screenshot_as_file('static/' + name)

    return name


with open('input-test-dup.csv', 'r') as input, \
    open('output.csv', 'w') as output:

    fieldnames=['topic','name','site', 'screenshot', 'description', \
        'publication', 'query', 'doi','title']

    reader = csv.DictReader(input)
    writer = csv.DictWriter(output, fieldnames=fieldnames)

    writer.writeheader()

    count = 1

    apps = set()
    
    for line in reader: 

        # GET DATASET NAME 
        doi = line['doi']
        doi = doi.split("g/")[1]
        
        url = "https://api.datacite.org/dois/" + doi

        headers = {"Accept": "application/vnd.api+json"}

        response = requests.request("GET", url, headers=headers)

        title = response.json()['data']['attributes']['titles'][0]

        print(title['title'])
        
        line['title'] = title['title']

       
        # GET SITE SCREENSHOT

        # handles duplicates
        if line['name'] not in apps:
            line['screenshot'] = get_snapshot(line['site'], count)
            # line['id'] = str(count)
            count += 1
        

        # GET APP DESCRIPTION
        req = requests.get(line['site'])
        soup = BeautifulSoup(req.text, 'html5lib')
        topics = ['map', 'model', 'product', 'NASA', 'flood', 'fire', 'landslide'] # and more
        for p in soup.find_all('p'):
            for topic in topics:
                if topic in p.get_text():
                    sentence = p.get_text().split('.')
                    
        # line['description'] = sentence[0]

        # add app to set
        apps.add(line['name'])
        
        
        writer.writerow(line)

