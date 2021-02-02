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
    parser.add_argument('-i', '--ifile', default='algo-output.csv',
        metavar="input-pathname")
    return parser.parse_args()

def db_input_csv(input_file):
    """reads the input CSV file and loads into the neptune database
    Positional Arguments:
    input_file:  input CSV file
    neptune_endpoint: secure web socket Neptune endpoint
    """
    db = GraphDB()
    # load csv file
    with open(input_file, 'r') as file:
        # initiate csv reader
        reader = csv.DictReader(file)
        # loop through every line in csv file
        for line in reader:
            print("Onto the Next One")
            print(db.add_app(line))
            print(db.add_dataset(line))
            print(db.add_relationship(line['name'], line['doi']))
    # counts vertices, used for troubleshooting purposes
    print(db.get_vertex_count())
    #print("Vertices count: " + {graph_trav.V().count().next()}, file=sys.stderr)

if __name__ == '__main__':
    # Main program
    args = parse_options()
    db_input_csv(args.ifile)
