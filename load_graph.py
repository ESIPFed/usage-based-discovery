#!/usr/bin/env python
"""load_graph.py 
Load a set of application-dataset relationships in CSV form into a Neptune graph database
"""

from __future__  import print_function  # Python 2/3 compatibility
import csv
import sys
import os
import argparse

from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
# from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

from gremlin_python.process.traversal import Bindings


def parse_options():
    """parse the command line options, returning input file and Neptune endpoint"""
    parser = argparse.ArgumentParser(description="Load CSV input into UBD Neptune database")
    parser.add_argument('-i', '--ifile', default='algo-output.csv',
        metavar="input-pathname")
    parser.add_argument('-n', '--neptune',
        metavar="neptune-endpoint")
    return parser.parse_args()


def load_database(input_file, neptune_endpoint):
    """reads the input CSV file and loads into the neptune database
    Positional Arguments:
    input_file:  input CSV file
    neptune_endpoint: secure web socket Neptune endpoint
    """

    # initiate connection
    graph = Graph()

    # Neptune secure web sockets endpoint, e.g.
    # wss://neptunedbinstance-gobble.dygook.us-west-1.neptune.amazonaws.com:8182/gremlin
    if neptune_endpoint is None:
        neptune_endpoint = os.environ.get('NEPTUNEDBRO')
        if neptune_endpoint is None:
            sys.exit("Neptune Endpoint was not supplied in either command line or NEPTUNEDBRO environment")
    remote_connection = DriverRemoteConnection(neptune_endpoint, 'g')
    graph_trav = graph.traversal().withRemote(remote_connection)

    # start loading graph

    empty = False
    # clear graph
    try:
        graph_trav.V().drop().iterate()
    except:
        empty = True
        print("No existing graphs to clear", file=sys.stderr)
        names = []
        titles = []

    # load csv file
    with open(input_file, 'r') as file:

        # initiate csv reader
        reader = csv.DictReader(file)

        # loop through every line in csv file
        for line in reader:

            # generates a list of existing applications and datasets to avoid duplicates
            if not empty:
                names = graph_trav.V().name.toList()
                titles = graph_trav.V().title.toList()

            # this conditional checks for application duplicates
            if line['name'] not in names:
                # if application is not yet in database, add it
                app_vertex = graph_trav.addV('application').property('topic', line['topic']) \
                   .property('name', line['name']) \
                   .property('site', line['site']) \
                   .property('screenshot', line['screenshot']) \
                   .property('publication', line['publication'])  \
                   .property('description', line['description']).next()
            else:
                print(f"{line['name']} already in db, skipping...", file=sys.stderr)
                # else, get existing application vertex
                app_vertex = graph_trav.V().has('application', 'name', line['name']).limit(1)

            # this conditional checks for dataset duplicates
            if line['title'] not in titles:
                # if dataset is not yet in database, add it
                dataset_vertex = graph_trav.addV('dataset') \
                    .property('doi', line['doi']) \
                    .property('title', line['title']).next()
            else:
                # else, get existing dataset vertex
                dataset_vertex = graph_trav.V().has('dataset', 'title', line['title']).limit(1)

            # add edge between application and dataset vertices
            graph_trav.addE('uses').from_(app_vertex).to(dataset_vertex).iterate()


    # counts vertices, used for troubleshooting purposes
    print(f"Vertices count: {graph_trav.V().count().next()}", file=sys.stderr)

    # close connection
    # remote_connection.close()

    return graph_trav

# Main program
args = parse_options()
load_database(args.ifile, args.neptune)
