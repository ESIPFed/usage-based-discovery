from bs4 import BeautifulSoup
import requests, re, html5lib
import urllib.request
import xml.etree.ElementTree as ET
from urllib.request import urlopen


#url = "https://floodobservatory.colorado.edu/"
#url = "https://gpm.nasa.gov/applications/global-landslide-model"
url = "http://flood.umd.edu/"
req = requests.get(url)
soup = BeautifulSoup(req.text, 'html.parser')
#haven't really done super extensive tests, but here are a few options. from the fires perspective, 1 and 3 seem to work the best, but we can always
#modify with other application topics. 
#feel free to replace any of the key words with common ones found in floods!
keywords = ['NASA', 'fire', 'flood', 'landslide']
string = ""
output = ""
for p in BeautifulSoup(req.text, 'html5lib').find_all('p'):
    string += p.get_text()




#option 1 - finds the topic present in the application, then extracts the first instance that the topic name is found in  
topics = ['fire', 'flood', 'landslide']
for p in soup.find_all('p'):
    for topic in topics:
        if topic in p.get_text():
            sentence = p.get_text().split('.')
for topic in topics:
    for item in sentence:
        if topic in item:
            print(item)
#print(sentence, '\n')       
'''#option 2 - extracts the sentence where the first key word was found 

potential_keywords = ['aerosol', 'optical', 'depth', 'aod', 'aot', 'thickness', 'area', 'scar', 
    'active', 'fire', 'plume', 'height', 'smoke', 'detection', 'air','quality', 'volcano', 'scar', 
    'severity', 'vegetation']
description = []
output = ''
for p in soup.find_all('p'):
    for name in potential_keywords:
        if name in p.get_text().lower():
            description = p.get_text().split('.')
        for sentence in description:
            if name in sentence:
                output = sentence
#print(output, '\n')

#option 3 - find the title of the application, and wherever the word of the title appears, extract that sentence 
title = soup.find('title').get_text()
titlesplit = title.split(' ')
word = titlesplit[0]
title_sample=[]
for p in soup.find_all('p'):
    if word in p.get_text():
        title_sample.append(p.get_text().split('.'))
example = title_sample[0][0]
print(example, '\n') 
'''