import requests
from bs4 import BeautifulSoup
import re
import xml.etree.ElementTree as ET
from w3lib.html import remove_tags
import json
from s3_functions import s3Functions

s3 = s3Functions()
data = s3.get_file('test-bucket-parth', 'facets.json')
data = json.loads(data)

instrument_names = data['relations'].keys()
platform_names = data['platforms']
platform_instrument_relations = data['relations']

list_of_shortNames = ["MCD14DL", "MCD14ML","VNP14", "MCD64A1", "MOD14", "MOD14A1",
    "MOD14A2", "MYD14", "MYD14A1", "MYD14A2", "VNP03MODLL", "VNP14", "VNP14A1",
    "VNP64A1", "MCD12Q1"]

application_topics = ['flood', 'fire', 'landslide', 'water', 'air', 'hurricane',
    'cyclone', 'snowfall', 'lake height', 'agriculture', 'hazard', 'earthquake',
    'energy', 'soil moisture', 'storm', 'precipitation', 'river height', 'volcanoe']

keywords = ['hurricane', 'earthquake', 'landslide', 'fire', 'flood',
    'air', 'water', 'lightning', 'snow', 'volcano', 'cloud', 'ocean']

measurements = ['aerosol optical depth', 'aod', 'aot', 'burn severity', 'air pollution',
    'plume height', 'air quality',  'water quality', 'smoke detection', 'active fire']

natural_phenomenons = ['hurricane', 'earthquake', 'landslide', 'fire', 'flood',
    'air', 'water', 'lightning', 'snow', 'volcano', 'cloud', 'ocean']

general_measurements = ['thickness', 'humidity', 'temperature', 'surface', 'precipitation']

def get_descriptive_words(data):
    specific_measure = ''
    phenomenon = []
    measurement = ''
    keyword = ''
    for name in measurements:
        if name in data.lower():
            specific_measure = name
    if len(specific_measure) != 0:
        return specific_measure
    #combine the general measurements and natural phenomenons to get a more specific search 
    if len(phenomenon) != 0 and len(measurement) != 0:
        return phenomenon[0] + "+" + measurement
    elif len(phenomenon) != 0:
        return phenomenon[0]

def convert_cmr_query(query):
    stub = "https://search.earthdata.nasa.gov/search?"
    query = query.replace('https://cmr.earthdata.nasa.gov/search/collections?', stub)
    query = query.replace('+', '%20')
    query = query.replace('&keyword=', '&q=')
    query = query.replace('&instrument=', '&fi=', 1)
    query = query.replace('&instrument=', '!')
    query = query.replace('&platform=', '&fp=', 1)
    query = query.replace('&platform=', '!')
    query = query.replace('&collection_data_type=NEAR_REAL_TIME', '&ff=Near Real Time')
    query = query.replace(' ', '%20')
    return query

def get_dataset(url, nrt, descriptive_words):
    url = re.sub(" ", "%20", url)
    descriptive_words = re.sub(" ", "%20", descriptive_words)
    response = requests.get(url)
    root = ET.fromstring(response.content)
    hits = int(root.find("hits").text)
    if hits == 0:
        return None
    
    if nrt:
        nrt_url = url + "&collection_data_type=NEAR_REAL_TIME"
        nrt_response = requests.get(nrt_url)
        nrt_root = ET.fromstring(nrt_response.content)
        nrt_hits = int(nrt_root.find("hits").text)
        if nrt_hits != 0:
            url = nrt_url
            response = nrt_response
            root = nrt_root
            hits = nrt_hits
    
    descriptive_words = re.sub(" ", "%20", descriptive_words)
    desc_url = url + "&keyword=" + descriptive_words
    desc_response = requests.get(desc_url)
    desc_root = ET.fromstring(desc_response.content)
    desc_hits = int(desc_root.find("hits").text)
    if desc_hits != 0:
        url = desc_url
        response = desc_response
        root = desc_root
        hits = desc_hits

    if hits > 15:
        return None
    datasets = []
    for reference in root.find('references'):
        dataset_title = ""
        dataset_link = ""
        for elem in reference:
            if elem.tag == 'name':
                dataset_title = elem.text
            if elem.tag == 'location':
                dataset_link = elem.text
        datasets.append((dataset_title, dataset_link, convert_cmr_query(url)))
    return datasets

def get_datasets(keywords):

    cmr_url = 'https://cmr.earthdata.nasa.gov/search/collections?' 
    queries = []

    for shortname in keywords['shortnames']:
        queries.append(base_url + 'short_name=' + shortname)

    covered_platforms = set()

    #only add to the query link if the instrument and platform go together
    for instrument in keywords['instruments']:
        url = cmr_url + "&instrument=" + instrument
        for platform in keywords['platforms']:
            if instrument in platform_instrument_relations.keys():
                if platform in platform_instrument_relations[instrument]:
                    url = url + "&platform=" + platform
                    covered_platforms.add(platform)
        queries.append(url)

    #if the instrument name doesn't exist, then add the platform name 
    for platform in keywords['platforms']:
        if platform not in covered_platforms:
            url = cmr_url + '&platform=' + platform
            queries.append(url)

    '''
    for word in keywords['other']:
        url = cmr_url + "&keyword=" + word
        queries.append(url)
    '''

    #removes duplicate query links
    queries = list(dict.fromkeys(queries))
    datasets = []
    for i in range(0, len(queries)):
        result = get_dataset(queries[i], keywords['nrt'], keywords['descriptive'])
        if result:
            datasets += result
    return datasets

def get_shortNames(soup, data):
    shortNames = []
    for name in list_of_shortNames:
        if name in data:
            shortNames.append(name)
    #some applications may have the shortname as a hyperlink 
    for link in soup.find_all('a'):
        for name in list_of_shortNames:
            if name == link.get_text():
                shortNames.append(name)
    return shortNames

def get_instruments(data):
    instruments = []
    for name in instrument_names:
        if re.search("(?<=[^a-zA-Z])"+name.lower()+"(?=[^a-zA-Z])",data.lower()):
            instruments.append(name)
    return instruments

def get_platforms(data):
    platforms = []
    for name in platform_names:
        if re.search("(?<=[^a-zA-Z])"+name.lower()+"(?=[^a-zA-Z])",data.lower()):
            platforms.append(name)
    return platforms

def get_nrt(data):
    data = data.lower()
    if re.search("near real|nrt|real time|real-time", data):
        return True
    return False

def get_topic(data):
    app_topic = []
    topic = ''
    for topic in application_topics:
        if topic in data.lower():
            app_topic.append(topic)
    if len(app_topic) != 0:
        #included as a stylistic choice (more aesthetic for front-end) 
        #wasn't able to get the list comparison to work with certain topics 
        if app_topic != 'air' or app_topic != 'energy' or app_topic != 'ecology' or app_topic != 'water':
            topic = app_topic[0].capitalize() + "s"
    else:
        topic = "Miscellaneous"
    return topic 

#gets the name of the application 
def get_application_title(soup):
    title = soup.title.text
    return title 

def get_sentences(data):
    sentences = re.split("(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", data)
    return sentences

def get_words(data):
    words = set(re.split("[^\w-]+", data))
    return words

def get_description(sentences):
    description = ""
    for sentence in sentences:
        if len(re.split("\s", sentence)) > 5 and len(re.findall("\.", sentence)) < 3:
            found = False
            for keyword in keywords:
                if not found and keyword in sentence.lower():
                    description += sentence + " "
                    found = True
    return description.strip()

def get_publications(sentences, soup):
    publications = []
    websites = soup.findAll('a', attrs={'href': re.compile("^http")})
    for link in websites:
        if 'doi' in link['href'] and link['href'] not in publications:
            publications.append(link['href'])
    for sentence in sentences:
        if 'doi:' in sentence:
            sentence = sentence[sentence.find('doi'):]
            sentence = sentence.replace("doi:", "https://doi.org/")
            if sentence[-1] == '.':
                sentence = sentence[:-1]
            if sentence not in publications:
                publications.append(sentence)
    return publications

def get_other(data, keywords):
    other = []
    words = get_words(data)
    for word in words:
        if re.match("[A-Z]{3,8}_*\d*[A-Z]*\d*", word) and word not in keywords:
            other.append(word)
    return other

def get_keywords(data, soup):
    keywords = {'instruments': [], 'platforms': [], 'shortnames': [], 'nrt': False, 'other': []}
    keywords['instruments'] = get_instruments(data)
    keywords['platforms'] = get_platforms(data)
    keywords['shortnames'] = get_shortNames(soup, data)
    keywords['nrt'] = get_nrt(data)
    keywords['other'] = get_other(data, keywords['instruments']+keywords['platforms']+keywords['shortnames'])
    keywords['descriptive'] = get_descriptive_words(data)
    return keywords

def makedict(site, soup, data):
    sentences = get_sentences(data)
    result = {}
    result['site'] = site
    result['topic'] = get_topic(data)
    result['name'] = get_application_title(soup)
    result['description'] = get_description(sentences)
    result['publications'] = get_publications(sentences, soup)
    result['keywords'] = get_keywords(data, soup)
    result['datasets'] = get_datasets(result['keywords'])
    return result

def autofill(url):
    print(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser') #contains all of the tags, raw HTML 
    data = soup.get_text()
    #remove html entities like &#13;
    data = re.sub("&\W*\w{2,4};", "", data)
    data = re.sub("\s\s+", " ", data)
    result = makedict(url, soup, data)
    print(json.dumps(result, indent=4))
    return result
