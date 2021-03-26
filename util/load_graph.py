#!/usr/bin/env python
"""
load_graph.py
Load a set of application-dataset relationships in CSV form into a Neptune graph database
"""
import csv
import argparse
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
    graph.clear_database()
    with open(input_file, 'r') as file:
        # initiate csv reader
        reader = csv.DictReader(file)
        # loop through every line in csv file
        for line in reader:
            print("Onto the Next One")
            line['topic'] = [line['topic'], 'test']
            print(line['topic'])
            print(graph.add_app(line))
            print(graph.add_dataset(line))
            print(graph.add_relationship(line['name'], line['doi']))
    # counts vertices, used for troubleshooting purposes
    print(graph.get_vertex_count())
    print(graph.get_edge_count())

if __name__ == '__main__':
    args = parse_options()
    db_input_csv(args.ifile)
