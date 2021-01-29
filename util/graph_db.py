#!/usr/bin/env python
from __future__  import print_function  # Python 2/3 compatibility
import csv
import sys
import os
import argparse
import asyncio
from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import *
from gremlin_python.process.graph_traversal import __
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.traversal import Bindings
# from gremlin_python.process.strategies import *

class GraphDB:
    
    def __init__(self):
        # initiate connection
        self.graph = Graph()
        # Neptune secure web sockets endpoint, e.g.
        neptune_endpoint = os.environ.get('NEPTUNEDBRO')
        if neptune_endpoint is None:
            sys.exit("Neptune Endpoint was not supplied in NEPTUNEDBRO environment")
        if not self.valid_endpoint(neptune_endpoint):
            sys.exit("Invalid Neptune Endpoint")
        self.remote_connection = DriverRemoteConnection(neptune_endpoint, 'g')
        self.graph_trav = self.graph.traversal().withRemote(self.remote_connection)

    def __del__(self):
        print("I am terminating the connection!")
        self.remote_connection.close()

    def valid_endpoint(self, neptune_endpoint):
        return neptune_endpoint.startswith("wss://") and neptune_endpoint.endswith(":8182/gremlin")

    def has_app(self, name):
        return self.graph_trav.V().has('application', 'name', name).limit(1)

    def has_dataset(self, doi):
        return self.graph_trav.V().has('dataset', 'doi', doi).limit(1)

    async def get_topics(self):
        '''
        queries database for a set of all topics
        '''
        topics = self.graph_trav.V().hasLabel('application').values('topic').toSet()
        print(topics)
        return topics 

    def get_apps_by_topic(self, topic):
        '''
        queries database for a list of all applications related to the given topic
        '''
        return self.graph_trav.V().has('application', 'topic', topic).elementMap().toList()

    def get_datasets_by_topic(self, topic):
        '''
        queries database for a list of datasets related to the given topic
        '''
        return self.graph_trav.V().has('application', 'topic', topic).out().elementMap().toList()

    def get_datasets_by_app(self, app):
        '''
        queries database for a list of datasets that the given application might be using
        '''
        return self.graph_trav.V().has('application', 'name', app).out().elementMap().toList()
    
    def add_app(self, app):
        '''
        adds application to database if it doesn't already exist
        '''
        return self.graph_trav.V().has('application', 'name', app['name']).fold().coalesce(unfold(), addV('application') \
            .property('topic', app['topic']) \
            .property('name', app['name']) \
            .property('site', app['site']) \
            .property('screenshot', app['screenshot']) \
            .property('publication', app['publication'])  \
            .property('description', app['description'])).next()

    def add_dataset(self, dataset):
        '''
        adds dataset to database if it doesn't already exist
        '''
        return self.graph_trav.V().has('dataset', 'doi', dataset['doi']).fold().coalesce(unfold(), addV('dataset') \
            .property('doi', dataset['doi']) \
            .property('title', dataset['title'])).next()

    def add_relationship(self, name, doi):
        '''
        adds relationship to database if it doesn't already exist
        '''
        return self.graph_trav.V().has('application', 'name', name).as_('v') \
                .V().has('dataset', 'doi', doi) \
                .coalesce(inE('uses').where(outV().as_('v')), addE('uses').from_('v')).next()
    
    async def get_vertex_count(self):
        return self.graph_trav.V().count().next()


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
    print(asyncio.run(db.get_vertex_count()))
    #print("Vertices count: " + {graph_trav.V().count().next()}, file=sys.stderr)

if __name__ == '__main__':
    # Main program
    args = parse_options()
    db_input_csv(args.ifile)
