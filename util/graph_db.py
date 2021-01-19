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
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.traversal import Bindings
# from gremlin_python.process.strategies import *


def parse_options():
    """parse the command line options, returning input file and Neptune endpoint"""
    parser = argparse.ArgumentParser(description="Load CSV input into UBD Neptune database")
    parser.add_argument('-i', '--ifile', default='algo-output.csv',
        metavar="input-pathname")
    parser.add_argument('-n', '--neptune',
        metavar="neptune-endpoint")
    return parser.parse_args()

def connect(neptune_endpoint):
    # initiate connection
    graph = Graph()
    # Neptune secure web sockets endpoint, e.g.
    if neptune_endpoint is None:
        neptune_endpoint = os.environ.get('NEPTUNEDBRO')
        if neptune_endpoint is None:
            sys.exit("Neptune Endpoint was not supplied in either command line or NEPTUNEDBRO environment")
    remote_connection = DriverRemoteConnection(neptune_endpoint, 'g')
    return graph.traversal().withRemote(remote_connection)

def get_topics(graph_trav):
    '''
    queries database for a set of all topics
    '''
    return graph_trav.V().hasLabel('application').values('topic').toSet()

def get_topic_apps(graph_trav, topic):
    '''
    queries database for a list of all applications related to the given topic
    '''
    return graph_trav.V().has('application', 'topic', topic).elementMap().toList()

def get_topic_datasets(graph_trav, topic):
    '''
    queries database for a list of datasets related to the given topic 
    '''
    return graph_trav.V().has('application', 'topic', topic).out().elementMap().toList()

def get_app_datasets(graph_trav, app):
    '''
    queries database for a list of datasets that the given application might be using
    '''
    return graph_trav.V().has('application', 'name', app).out().elementMap().toList()



# maybe write a class and get rid of graph_trav input
def add_app(graph_trav, line, names):
    # name may be an unecessary input
    # should be able to query graph db for does line['name'] already exist
    # this conditional checks for application duplicates
    if line['name'] not in names:
        # if application is not yet in database, add it
        return graph_trav.addV('application').property('topic', line['topic']) \
            .property('name', line['name']) \
            .property('site', line['site']) \
            .property('screenshot', line['screenshot']) \
            .property('publication', line['publication'])  \
            .property('description', line['description']).next()
    print( line['name'] + " already in db, skipping...", file=sys.stderr)
    # get existing application vertex
    return graph_trav.V().has('application', 'name', line['name']).limit(1)

def add_dataset(graph_trav, line, titles):
    # this conditional checks for dataset duplicates
    if line['title'] not in titles:
        # if dataset is not yet in database, add it
        return graph_trav.addV('dataset') \
            .property('doi', line['doi']) \
            .property('title', line['title']).next()
    # get existing dataset vertex
    return graph_trav.V().has('dataset', 'title', line['title']).limit(1)


def db_input_csv(input_file, neptune_endpoint):
    """reads the input CSV file and loads into the neptune database
    Positional Arguments:
    input_file:  input CSV file
    neptune_endpoint: secure web socket Neptune endpoint
    """
    graph_trav = db_connect(neptune_endpoint)
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
            
            app_vertex = add_app(graph_trav, line, names)
            dataset_vertex = add_dataset(graph_trav, line, titles)

            # add edge between application and dataset vertices
            graph_trav.addE('uses').from_(app_vertex).to(dataset_vertex).iterate()

    # counts vertices, used for troubleshooting purposes
    print("Vertices count: " + {graph_trav.V().count().next()}, file=sys.stderr)

    # close connection
    remote_connection.close()
    return graph_trav

if __name__ == '__main__':
    # Main program
    args = parse_options()
    db_input_csv(args.ifile, args.neptune)
