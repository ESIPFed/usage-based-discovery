#!/usr/bin/env python
"""
load_graph.py
Load a set of application-dataset relationships in CSV form into a Neptune graph database
"""
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
    parser.add_argument('-i', '--ifile', default='algo-output.csv', metavar="input-pathname")
    return parser.parse_args()

def db_input_csv(input_file):
    """reads the input CSV file and loads into the neptune database
    Positional Arguments:
    input_file:  input CSV file
    neptune_endpoint: secure web socket Neptune endpoint
    """
    graph = GraphDB()
    graph.clear_database()
    # load csv file
    with open(input_file, 'r') as file:
        # initiate csv reader
        reader = csv.DictReader(file)
        # loop through every line in csv file
        for line in reader:
            line['topic'] = re.sub("\]|\[|\'", '', line['topic'])
            line['topic'] = line['topic'].split(',')
            for index, t in enumerate(line['topic']):
                line['topic'][index] = t.strip()
                print(graph.add_topic(line['topic'][index]))
            if 'app_discoverer' in line.keys():
                graph.add_app(line, discoverer=line['app_discoverer'], verified='True'==line['app_verified'], verifier=line['app_verifier'])
                #graph.add_app(line, discoverer='0000-0002-3708-5496', verified=True, verifier='0000-0002-3708-5496')
            else: 
                graph.add_app(line)
            graph.add_dataset(line)
            if 'discoverer' in line.keys():
                print('new line:\n', line)
                print('verifier:\n', line['verified'])
                graph.add_relationship(line['name'], line['doi'], discoverer=line['discoverer'], verified='True'==line['verified'], verifier=line['verifier'], annotation=line['annotation'])
            else:
                graph.add_relationship(line['name'], line['doi'])
    # counts vertices, used for troubleshooting purposes
    print(graph.get_vertex_count())
    print(graph.get_edge_count())

if __name__ == '__main__':
    args = parse_options()
    db_input_csv(args.ifile)
