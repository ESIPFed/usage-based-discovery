
"""csv2ubd.py - convert DatasetArticles tab form to one loadable into UBD
python csv2ubd.py < DatasetArticles.csv > load_ubd.csv
Since normal foraging tables include multiple topics for each 
dataset-article line, they need to be "unwrapped" for loading into
the Usage-Based Discovery tool so that there is only one topic per line. 
The code also does some valids checking on the topics.
N.B.: uncertain topics (ending with '?') are not included by default.
Also, it expands "Biodiversity" to "Biodiversity + Ecosystem Function"
"""

import csv
import sys
import argparse

def parse_options():
    parser = argparse.ArgumentParser(description="Convert classification CSV for to UBD-compatible CSV")
    parser.add_argument('-m', '--maybe', action="store_true",
            help='if set, include uncertain classifications')
    return(parser.parse_args())

args = parse_options()
ubd_header = "topic,name,site,publication,description,title,doi,type,app_discoverer,app_verifier,app_verified,annotation,discoverer,verifier,verified,screenshot,essential_variable"
reader = csv.DictReader(sys.stdin)
writer = csv.writer(sys.stdout)
print(ubd_header)
legit_topics = [
    'Agriculture',
    'Aerosols',
    'Air Quality',
    'Atmospheric Chemistry',
    'Biodiversity + Ecosystem Function',
    'Climate',
    'Clouds + Water Vapor',
    'Cyclones',
    'Data Science',
    'Earthquakes',
    'Fire',
    'Floods',
    'Geodesy',
    'Human Activity',
    'Land Surface Properties',
    'Landslides',
    'Ocean Biology',
    'Ocean Chemistry',
    'Ocean Physics',
    'Precipitation',
    'Radiation + Energy Budget',
    'Sea Level', 
    'Snow + Ice',
    'Soil Properties',
    'Solid Earth',
    'Vegetation',
    'Volcanoes',
    'Water Resources',
    'Weather'
]
xlate_topics = {'Biodiversity':'Biodiversity + Ecosystem Function'}
n_out = 0
n_in = 0
articles = set()
# For each row in the CSV file (below the header)
for row in reader:
    n_in += 1

    articles.add(row['name'])
    
    for t in range(1, 7):
        t_col = f'topic-{t}'
        if t_col not in row:
            break

        if row[t_col] == "":
            break

        topic = row[t_col]

        if topic[-1] == "?" and not args.maybe:
            break

        if topic in xlate_topics:
            topic = xlate_topics[topic]
        if topic == "Other":
            break
        if topic not in legit_topics:
            print(f'Topic error at line {n_in+1}: {topic}; fix it!', file=sys.stderr)
            continue
        writer.writerow((topic, row['name'], row['website'], "", row['description'], row['ds_title'], row['ds_url'], "Research", row['orcid'], "", "true", "", "", "", "true", "", ""))
        n_out += 1

print(f'{n_in} records read, {len(articles)} articles', file=sys.stderr)
if n_out == 0:
    print("No records written!", file=sys.stderr)
    exit(1)
else:
    print(f'Wrote {n_out} records', file=sys.stderr)