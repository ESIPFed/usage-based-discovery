#!/usr/bin/env python
"""
load_graph.py
Load a set of application-dataset relationships in CSV form into a Neptune graph database
"""
from dotenv import load_dotenv
load_dotenv()
import sys
sys.path.append("../")
import csv
import argparse
import json
import re
from graph_db import GraphDB

def parse_options():
    """parse the command line options, returning input file and Neptune endpoint"""
    parser = argparse.ArgumentParser(description="Load CSV input into UBD Neptune database")
    parser.add_argument('-i', '--ifile', default='graph_snapshot.csv', metavar="input-pathname")
    return parser.parse_args()

def db_input_csv(input_file):
    """reads the input CSV file and loads into the neptune database
    Positional Arguments:
    input_file:  input CSV file
    neptune_endpoint: secure web socket Neptune endpoint
    """
    # TAKE A SNAPSHOT OF YOUR NEPTUNE DB BEFORE RUNNING
    graph = GraphDB()
    graph.clear_database()
    with open(input_file, 'r') as file:
        reader = csv.DictReader(file)
        for line in reader:
            # add a default classification
            # 'unclassified',
            # 'Software',
            # 'Research'
            if not 'type' in line.keys():
                line['type'] = 'unclassified'
            
            # parse topics (app can belong to many topics[])
            line['topic'] = re.sub("\]|\[|\'", '', line['topic'])
            line['topic'] = line['topic'].split(',')
            
            # parse types (app node can have multiple types[])
            line['type'] = re.sub("\]|\[|\'", '', line['type'])
            line['type'] = line['type'].split(',')
            
            # add each topic[], before adding the app
            for index, t in enumerate(line['topic']):
                line['topic'][index] = t.strip()
                print(graph.add_topic(line['topic'][index]))
            
            # add the application to the graph
            # columns: name, site, screenshot, publication, description, 
            # app_discoverer, app_verifier, app_verified, type[], topic[]
            if 'app_discoverer' in line.keys():
                graph.add_app(
                    app=line, 
                    discoverer=line['app_discoverer'], 
                    verified=('true'==line['app_verified'].lower()), 
                    verifier=line['app_verifier'])
            else: 
                # put your orcid Id in for discoverer and verifier
                graph.add_app(
                    app=line, 
                    discoverer='0000-0002-3708-5496', 
                    verified=True, 
                    verifier='0000-0002-3708-5496') 
            
            # add the dataset to the graph
            # columns: doi, title
            graph.add_dataset(dataset=line)
            
            # connect the dataset to the app
            # columns: annotation, discoverer, verifier, verified
            if 'discoverer' in line.keys():
                print('new line:\n', line)
                print('verifier:\n', line['verified'])
                graph.add_relationship(
                    site=line['site'], 
                    doi=line['doi'], 
                    discoverer=line['discoverer'], 
                    verified='true'==line['verified'].lower(), 
                    verifier=line['verifier'], 
                    annotation=line['annotation'])
            else:
                graph.add_relationship(site=line['site'], doi=line['doi'])
    
    # counts vertices, used for troubleshooting purposes
    print(graph.get_vertex_count())
    print(graph.get_edge_count())

if __name__ == '__main__':
    args = parse_options()
    db_input_csv(args.ifile)
