#!/usr/bin/env python
from __future__  import print_function  # Python 2/3 compatibility
import os
import sys
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
        graph = Graph()
        # Neptune secure web sockets endpoint, e.g.
        neptune_endpoint = os.environ.get('NEPTUNEDBRO')
        if neptune_endpoint is None:
            sys.exit("Neptune Endpoint was not supplied in NEPTUNEDBRO environment")
        if not self.valid_endpoint(neptune_endpoint):
            sys.exit("Invalid Neptune Endpoint")
        self.remote_connection = DriverRemoteConnection(neptune_endpoint, 'g')
        self.graph_trav = graph.traversal().withRemote(self.remote_connection)

    def __del__(self):
        print("I am terminating the connection!")
        self.remote_connection.close()
    
    def valid_endpoint(self, neptune_endpoint):
        return neptune_endpoint.startswith("wss://") and neptune_endpoint.endswith(":8182/gremlin")

    def has_app(self, name):
        '''
        returns true if the app name is found in the database
        otherwise false
        '''
        return self.graph_trav.V().has('application', 'name', name).hasNext()

    def has_dataset(self, doi):
        '''
        returns true if the dataset doi is found in the database
        otherwise false
        '''
        return self.graph_trav.V().has('dataset', 'doi', doi).hasNext()

    def has_relationship(self, name, doi):
        return self.graph_trav.V().has('application', 'name', name).as_('v').V().has('dataset', 'doi', doi).inE('uses').hasNext()

    def get_topics(self):
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

    def get_datasets_by_app(self, name):
        '''
        queries database for a list of datasets that are connected to the given application
        '''
        return self.graph_trav.V().has('application', 'name', name).out().elementMap().toList()
    
    def get_vertex_count(self):
        '''
        returns number of vertexes in the database
        a nice sanity check if you will
        '''
        return self.graph_trav.V().count().next()
   
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
    
    def update_app(self, name):
        pass

    def update_doi(self, doi):
        pass

    def clear_database(self):
        '''
        warning: this function clears everything in the database
        '''
        return self.graph_trav.V().drop().iterate()

    def delete_application(self, name):
        pass

    def delete_dataset(self, doi):
        pass

    def delete_relationship(self, name, doi):
        pass


