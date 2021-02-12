#!/usr/bin/env python
'''
GraphDB: facilitates all interactions to the Neptune Graph Database
'''
from __future__  import print_function  # Python 2/3 compatibility
import os
import sys
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import unfold, inE, addV, addE, outV
from gremlin_python.process.traversal import Cardinality
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

def valid_endpoint(endpoint):
    '''
    checks whether or not the neptune_endpoint supplied is valid
    '''
<<<<<<< HEAD
    return (endpoint.startswith("wss://") or endpoint.startswith("ws://")) and endpoint.endswith(":8182/gremlin")
=======
    return (neptune_endpoint.startswith("wss://") or neptune_endpoint.startswith("ws://")) and neptune_endpoint.endswith(":8182/gremlin")
>>>>>>> upstream/main

class GraphDB:
    '''
    GraphDB: facilitates all interactions to the Neptune Graph Database
    '''
    def __init__(self):
        '''
        connects to the neptune database upon class creation
        '''
        graph = Graph()
        neptune_endpoint = os.environ.get('NEPTUNEDBRO')
        if neptune_endpoint is None:
            sys.exit("Neptune Endpoint was not supplied in NEPTUNEDBRO environment")
        if not valid_endpoint(neptune_endpoint):
            sys.exit("Invalid Neptune Endpoint")
        self.remote_connection = DriverRemoteConnection(neptune_endpoint, 'g')
        self.graph_trav = graph.traversal().withRemote(self.remote_connection)

    def __del__(self):
        '''
        disconnects from the neptune database once there are no more references to the class
        '''
        print("I am terminating the connection!")
        self.remote_connection.close()

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
        '''
        returns true if the relationship edge is found in the database
        otherwise false
        '''
        return self.graph_trav.V().has('application', 'name', name).as_('v').V() \
                .has('dataset', 'doi', doi).inE('uses').hasNext()

    def get_topics(self):
        '''
        queries database for a set of all topics
        '''
        topics = self.graph_trav.V().hasLabel('application').values('topic').toSet()
        return topics

    def get_app(self, name):
        '''
        queries database for a specific application
        '''
        return self.graph_trav.V().has('application', 'name', name).elementMap().toList()

    def get_dataset(self, doi):
        '''
        queries database for a specific database
        '''
        return self.graph_trav.V().has('dataset','doi', doi).elementMap().toList()

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

    def get_edge_count(self):
        '''
        returns number of edges in the database
        another nice sanity check if you will
        '''
        return self.graph_trav.E().count().next()

    def add_app(self, app):
        '''
        adds application to database if it doesn't already exist
        '''
        return self.graph_trav.V().has('application', 'name', app['name']) \
                .fold().coalesce(unfold(), addV('application') \
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
        return self.graph_trav.V().has('dataset', 'doi', dataset['doi']) \
                .fold().coalesce(unfold(), addV('dataset') \
                .property('doi', dataset['doi']) \
                .property('title', dataset['title'])).next()

    def add_relationship(self, name, doi):
        '''
        adds relationship to database if it doesn't already exist
        '''
        return self.graph_trav.V().has('application', 'name', name).as_('v') \
                .V().has('dataset', 'doi', doi) \
                .coalesce(inE('uses').where(outV().as_('v')), addE('uses').from_('v')).next()

    def update_app(self, name, app):
        '''
        updates application vertex in the database with new information
        '''
        return self.graph_trav.V().has('application', 'name', name) \
            .property(Cardinality.single, 'topic', app['topic']) \
            .property(Cardinality.single, 'name', app['name']) \
            .property(Cardinality.single, 'site', app['site']) \
            .property(Cardinality.single, 'screenshot', app['screenshot']) \
            .property(Cardinality.single, 'publication', app['publication'])  \
            .property(Cardinality.single, 'description', app['description']).next()

    def update_app_property(self, name, prop, value):
        '''
        updates only one of the application's properties
        '''
        if prop not in ['topic', 'name', 'site', 'screenshot', 'publication', 'description']:
            raise Exception("property provided is not a valid option")
        return self.graph_trav.V().has('application', 'name', name) \
                .property(Cardinality.single, prop, value).next()

    def update_dataset(self, doi, dataset):
        '''
        updates dataset vertex in the database with new information
        '''
        return self.graph_trav.V().has('dataset', 'doi', doi) \
                .property(Cardinality.single, 'title', dataset['title']) \
                .property(Cardinality.single, 'doi', dataset['doi']).next()

    def clear_database(self):
        '''
        warning: this function clears everything in the database
        '''
        return self.graph_trav.V().drop().iterate()

    def delete_app(self, name):
        '''
        deletes application vertex in the database
        '''
        return self.graph_trav.V().has('application', 'name', name).drop().iterate()

    def delete_dataset(self, doi):
        '''
        deletes dataset vertex in the database
        '''
        return self.graph_trav.V().has('dataset', 'doi', doi).drop().iterate()
