#!/usr/bin/env python
'''
GraphDB: facilitates all interactions to the Neptune Graph Database
'''
from __future__  import print_function  # Python 2/3 compatibility
import os   
import sys
#from util.env_loader import load_env
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import unfold, inE, addV, addE, outV, otherV, bothE, __
from gremlin_python.process.traversal import Cardinality, T, Direction, P
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

def valid_endpoint(endpoint):
    '''
    checks whether or not the neptune_endpoint supplied is valid
    '''
    return (endpoint.startswith("wss://") or endpoint.startswith("ws://")) and endpoint.endswith(":8182/gremlin")

class GraphDB:
    '''
    GraphDB: facilitates all interactions to the Neptune Graph Database
    '''
    def __init__(self):
        '''
        connects to the neptune database upon class creation
        '''
        #load_env()
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

    def get_data(self):
        '''
        queries database for all vertices and edges
        reformats the data for d3 network visualization
        returns dict containing nodes and links
        '''
        vertices = self.graph_trav.V().valueMap(True).toList()
        for v in vertices:
            v['id'] = v.pop(T.id)
            v['label'] = v.pop(T.label)
        edges = self.graph_trav.E().elementMap().toList()
        for e in edges:
            e['id'] = e.pop(T.id)
            e['label'] = e.pop(T.label)
            edge = e.pop(Direction.OUT)
            e['source'] = edge[T.id]
            edge = e.pop(Direction.IN)
            e['target'] = edge[T.id]
        return {'nodes': vertices, 'links': edges}

    def mapify(self, valuemap):
        for item in valuemap:
            for prop in item.keys():
                if len(item[prop]) == 1 and prop != 'topic':
                    item[prop] = item[prop][0]
        return valuemap

    def get_topics(self):
        '''
        queries database for a set of all topics
        '''
        return self.graph_trav.V().hasLabel('topic').values('topic').toSet()

    def get_app(self, name):
        '''
        queries database for a specific application
        '''
        return self.graph_trav.V().has('application', 'name', name).valueMap().toList()

    def get_dataset(self, doi):
        '''
        queries database for a specific database
        '''
        return self.graph_trav.V().has('dataset','doi', doi).valueMap().toList()

    def get_apps_by_topic(self, topic):
        '''
        queries database for a list of all applications related to the given topic
        '''
        return self.graph_trav.V().hasLabel('application').where(__.outE("about").otherV().has("topic", topic)).valueMap().toList()
    
    def get_app_topics(self, name):
        return self.graph_trav.V().has('application', 'name', name).out("about").values("topic").toList()

    def get_valid_apps_by_topic(self, topic):
        '''
        queries database for a list of all applications related to the given topic
        '''
        return self.graph_trav.V().hasLabel('application').where(__.outE("about").otherV().has("topic", topic).and_().outE().count().is_(P.gt(0))).valueMap().toList()

    def get_apps_without_screenshot(self):
        return self.graph_trav.V().has('application', 'screenshot', 'NA').valueMap().toList()

    def get_datasets_by_topic(self, topic):
        '''
        queries database for a list of datasets related to the given topic
        Sample return:
        [ path[
            { 'site': [''], 'publication': [''], 'name': [], 'publication': [], 'description': [] },
            { verified: True, orcid: '0000-0000-0000-0000' },
            { 'title': [''], 'doi': [''] }],
          path[ {APP}, {EDGE}, {DATASET} ] , ...]
        '''
        return self.graph_trav.V().hasLabel('application').where(__.outE("about").otherV().has("topic", topic)).outE('uses').inV().path().by(__.valueMap()).toList()

    def get_datasets_by_app(self, name):
        '''
        queries database for a list of datasets that are connected to the given application
        Sample return:
        [ path[
            { 'site': [''], 'publication': [''], 'name': [], 'publication': [], ... },
            { verified: True, orcid: '0000-0000-0000-0000' },
            { 'title': [''], 'doi': [''] }],
          path[ {APP}, {EDGE}, {DATASET} ], ... ]
        '''
        return self.graph_trav.V().has('application', 'name', name).outE('uses').inV().path().by(__.valueMap()).toList()

    def get_dataset_by_app(self, name, doi):
        '''
        queries database for a list of datasets that are connected to the given application
        Sample return:
        [ path[
            { 'site': [''], 'publication': [''], 'name': [], 'publication': [], ... },
            { verified: True, orcid: '0000-0000-0000-0000' },
            { 'title': [''], 'doi': [''] }]]
        '''
        return self.graph_trav.V().has('application', 'name', name).outE("uses").where(otherV().has("doi", doi)).inV().path().by(__.valueMap()).toList()

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

    def get_common_datasets(self):
        return self.graph_trav.V().hasLabel('dataset').where(bothE().count().is_(P.gte(4))).elementMap().toList()

    def add_app(self, app):
        '''
        adds application to database if it doesn't already exist
        sample input:
        {
            'topic': ['topic1', 'topic2', ...],
            'name': 'samplename',
            'site': 'https://example.com',
            'screenshot': 'image.png',
            'publication': 'publication',
            'description': 'sample description for a sample app'
        }
        '''
        self.graph_trav.V().has('application', 'name', app['name']) \
                .fold().coalesce(unfold(), addV('application') \
                .property('name', app['name']) \
                .property('site', app['site']) \
                .property('screenshot', app['screenshot']) \
                .property('publication', app['publication']) \
                .property('description', app['description'])).next()
        for i in range(len(app['topic'])):
            self.connect_topic(app['name'], app['topic'][i])

    def add_topic(self, topic):
        '''
        adds topic to database if it doesn't already exist
        '''
        return self.graph_trav.V().has('topic', 'topic', topic) \
                .fold().coalesce(unfold(), addV('topic') \
                .property('topic', topic)).next()

    def add_dataset(self, dataset):
        '''
        adds dataset to database if it doesn't already exist
        '''
        return self.graph_trav.V().has('dataset', 'doi', dataset['doi']) \
                .fold().coalesce(unfold(), addV('dataset') \
                .property('doi', dataset['doi']) \
                .property('title', dataset['title'])).next()

    def add_relationship(self, name, doi, discoverer="", verified=False, verifier="", annotation=""):
        '''
        adds relationship to database if it doesn't already exist
        '''
        return self.graph_trav.V().has('application', 'name', name).as_('v') \
                .V().has('dataset', 'doi', doi) \
                .coalesce(inE('uses').where(outV().as_('v')), addE('uses') \
                    .property('annotation', annotation) \
                    .property('discoverer', discoverer) \
                    .property('verified', verified) \
                    .property('verifier', verifier) \
                .from_('v')).next()

    def connect_topic(self, name, topic):
        '''
        adds relationship to database if it doesn't already exist
        '''
        return self.graph_trav.V().has('application', 'name', name).as_('v') \
                .V().has('topic', 'topic', topic) \
                .coalesce(inE('about').where(outV().as_('v')), addE('about') \
                .from_('v')).next()

    def add_app_property(self, name, prop, value):
        '''
        updates only one of the application's properties
        '''
        return self.graph_trav.V().has('application', 'name', name) \
                .property(Cardinality.set_, prop, value).next()

    def verify_relationship(self, name, doi, verifier):
        '''
        adds relationship to database if it doesn't already exist
        '''
        return self.graph_trav.V().has('name', name).outE("uses").where(otherV().has("doi", doi)) \
            .property('verified', True) \
            .property('verifier', verifier).next()

    def update_app(self, name, app):
        '''
        updates application vertex in the database with new information
        '''
        self.graph_trav.V().has('application', 'name', name) \
            .sideEffect(__.outE("about").where(otherV().hasLabel("topic")).drop()) \
            .property(Cardinality.single, 'name', app['name']) \
            .property(Cardinality.single, 'site', app['site']) \
            .property(Cardinality.single, 'screenshot', app['screenshot']) \
            .property(Cardinality.single, 'publication', app['publication']) \
            .property(Cardinality.single, 'description', app['description']).next()
        for i in range(len(app['topic'])):
            self.connect_topic(app['name'], app['topic'][i])

    def update_app_property(self, name, prop, value):
        '''
        updates only one of the application's properties
        if application property does not exist it will not do anything
        '''
        return self.graph_trav.V().has('application', 'name', name) \
                .property(Cardinality.single, prop, value).next()

    def update_dataset(self, doi, dataset):
        '''
        updates dataset vertex in the database with new information
        '''
        return self.graph_trav.V().has('dataset', 'doi', doi) \
                .property(Cardinality.single, 'title', dataset['title']) \
                .property(Cardinality.single, 'doi', dataset['doi']).next()

    def rename_topic(self, oldtopic, newtopic):
        return self.graph_trav.V().has('topic', 'topic', oldtopic) \
            .sideEffect(__.properties('topic').hasValue(oldtopic).drop()) \
            .property(Cardinality.set_,'topic', newtopic).iterate()

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

    def delete_relationship(self, name, doi):
        '''
        deletes relationship edge in the database
        '''
        return self.graph_trav.V().has('name', name).outE("uses").where(otherV().has("doi", doi)).drop().iterate();
    
    def delete_orphan_datasets(self):
        '''
        deletes all dataset vertexes in the database that have no connections
        '''
        return self.graph_trav.V().hasLabel('dataset').where(bothE().count().is_(0)).drop().iterate()
