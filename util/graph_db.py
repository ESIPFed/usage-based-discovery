#!/usr/bin/env python
'''
GraphDB: facilitates all interactions to the Neptune Graph Database
'''
from __future__  import print_function  # Python 2/3 compatibility
import os   
import sys
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import unfold, inE, addV, addE, outV, otherV, bothE, __
from gremlin_python.process.traversal import Cardinality, T, Direction, P, within
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.driver.tornado.transport import TornadoTransport
from util import essential_variables
from util import str_helper

def valid_endpoint(endpoint):
    '''
    checks whether or not the neptune_endpoint supplied is valid
    '''
    return (endpoint.startswith("wss://") or endpoint.startswith("ws://")) and endpoint.endswith(":8182/gremlin")

# Temp fix for: https://issues.apache.org/jira/browse/TINKERPOP-2388
class CustomTornadoTransport(TornadoTransport):
    def close(self):
        self._loop.run_sync(lambda: self._ws.close())
        message = self._loop.run_sync(lambda: self._ws.read_message())
        # This situation shouldn't really happen. Since the connection was closed,
        # the next message should be None
        if message is not None:
            raise RuntimeError("Connection was not properly closed")
        self._loop.close()

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
        self.remote_connection = DriverRemoteConnection(neptune_endpoint, 'g', transport_factory=CustomTornadoTransport)
        self.graph_trav = graph.traversal().withRemote(self.remote_connection)

    def __del__(self):
        '''
        disconnects from the neptune database once there are no more references to the class
        '''
        print("Closing neptune DB connection")
        if self.remote_connection is not None:
            self.remote_connection.close()

    def has_app(self, site):
        '''
        returns true if the app site is found in the database
        otherwise false
        '''
        return self.graph_trav.V().has('application', 'site', site).hasNext()

    def has_dataset(self, doi):
        '''
        returns true if the dataset doi is found in the database
        otherwise false
        '''
        return self.graph_trav.V().has('dataset', 'doi', doi).hasNext()

    def has_relationship(self, site, doi):
        '''
        returns true if the relationship edge is found in the database
        otherwise false
        '''
        return self.graph_trav.V().has('application', 'site', site).as_('v').V() \
                .has('dataset', 'doi', doi).inE('uses').hasNext()

    def get_all_data(self):
        '''
        queries database for all vertices and edges
        reformats the data for d3 network visualization
        returns dict containing nodes and links
        '''
        vertices = self.graph_trav.V().elementMap().toList()
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

    def get_data(self):
        '''
        queries database for only verified vertices and edges
        reformats the data for d3 network visualization
        returns dict containing nodes and links
        '''
        vertices = self.graph_trav.V().or_(__.has('application', 'verified', True), __.hasLabel('dataset').inE().has('uses', 'verified', True), __.hasLabel('topic')).valueMap(True).toList()
        for v in vertices:
            v['id'] = v.pop(T.id)
            v['label'] = v.pop(T.label)
        edges = self.graph_trav.E().or_(__.has('uses', 'verified', True).outV().has('application', 'verified', True), __.hasLabel('about').outV().has('application', 'verified', True)).elementMap().toList()
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
                if len(item[prop]) == 1 and prop != 'type' and prop != 'essential_variable':
                    item[prop] = item[prop][0]
        return valuemap

    def get_leader_board(self):
        return {
            'apps': self.graph_trav.V().hasLabel('application').valueMap().toList(),
            'uses': self.graph_trav.V().hasLabel('application').outE().hasLabel('uses').valueMap().toList()
        }

    def get_topics_by_types(self, types):
        return self.graph_trav.V().has('type', within(*types)).outE('about').otherV().values('topic').toSet()

    def get_types_by_topics(self, topics):
        return self.graph_trav.V().has('topic', within(*topics)).inE('about').otherV().values('type').toSet()

    def get_topics(self):
        '''
        queries database for a set of all topics
        '''
        return self.graph_trav.V().hasLabel('topic').values('topic').toList()

    def get_app(self, site):
        '''
        queries database for a specific application
        '''
        return self.graph_trav.V().has('application', 'site', site).valueMap().toList()

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
    
    def get_app_topics(self, site):
        return self.graph_trav.V().has('application', 'site', site).out("about").values("topic").toList()

    def get_valid_apps_by_topic(self, topic):
        '''
        queries database for a list of all applications related to the given topic
        '''
        return self.graph_trav.V().has('application', 'verified', True).where(__.outE("about").otherV().has("topic", topic).and_().outE().count().is_(P.gt(0))).valueMap().toList()

    def get_apps_without_screenshot(self):
        return self.graph_trav.V().has('application', 'screenshot', 'NA').valueMap().toList()

    def get_datasets_by_topic(self, topic):
        '''
        queries database for a list of datasets related to the given topic
        Sample return:
        [ path[
            { 'site': [''], 'publication': [''], 'name': [], 'publication': [], 'description': [], 'essential_variable': [] },
            { verified: True, orcid: '0000-0000-0000-0000' },
            { 'title': [''], 'doi': [''] }],
          path[ {APP}, {EDGE}, {DATASET} ] , ...]
        '''
        return self.graph_trav.V().hasLabel('application').where(__.outE("about").otherV().has("topic", topic)).outE('uses').inV().path().by(__.valueMap()).toList()

    def get_datasets_by_app(self, site):
        '''
        queries database for a list of datasets that are connected to the given application
        Sample return:
        [ path[
            { 'site': [''], 'publication': [''], 'name': [], 'publication': [], 'description': [], 'essential_variable': [] },
            { verified: True, orcid: '0000-0000-0000-0000' },
            { 'title': [''], 'doi': [''] }],
          path[ {APP}, {EDGE}, {DATASET} ], ... ]
        '''
        return self.graph_trav.V().has('application', 'site', site).outE('uses').inV().path().by(__.valueMap()).toList()

    def get_dataset_by_app(self, site, doi):
        '''
        queries database for a list of datasets that are connected to the given application
        Sample return:
        [ path[
            { 'site': [''], 'publication': [''], 'name': [], 'publication': [], ... },
            { verified: True, orcid: '0000-0000-0000-0000' },
            { 'title': [''], 'doi': [''] }]]
        '''
        return self.graph_trav.V().has('application', 'site', site).outE("uses").where(otherV().has("doi", doi)).inV().path().by(__.valueMap()).toList()

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

    def add_app(self, app, discoverer='', verified=False, verifier=''):
        '''
        adds application to database if it doesn't already exist
        sample input:
        {
            'topic': ['topic1', 'topic2', ...],
            'name': 'samplename',
            'site': 'https://example.com',
            'screenshot': 'image.png',
            'publication': 'publication',
            'description': 'sample description for a sample app',
            'essential_variable': ['Precipitation']
        }
        '''
        self.graph_trav.V().has('application', 'site', app['site']) \
                .fold().coalesce(unfold(), addV('application') \
                .property('name', app['name']) \
                .property('site', app['site']) \
                .property('screenshot', app['screenshot']) \
                .property('publication', app['publication']) \
                .property('description', app['description']) \
                .property('discoverer', discoverer) \
                .property('verified', verified) \
                .property('verifier', verifier)) \
                .next()
        for i in range(len(app['topic'])):
            self.connect_topic(app['site'], app['topic'][i])
        for i in range(len(app['type'])):
            self.add_app_property(app['site'], 'type', app['type'][i])
        if 'essential_variable' in app:
            for i in range(len(app['essential_variable'])):
                if app['essential_variable'][i] in essential_variables.values:
                    self.add_app_property(app['site'], 'essential_variable', app['essential_variable'][i])

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

    def add_relationship(self, site, doi, discoverer="", verified=False, verifier="", annotation=""):
        '''
        adds relationship to database if it doesn't already exist
        '''
        return self.graph_trav.V().has('application', 'site', site).as_('v') \
                .V().has('dataset', 'doi', doi) \
                .coalesce(inE('uses').where(outV().as_('v')), addE('uses') \
                    .property('annotation', annotation) \
                    .property('discoverer', discoverer) \
                    .property('verified', verified) \
                    .property('verifier', verifier) \
                .from_('v')).next()

    def connect_topic(self, site, topic):
        '''
        adds relationship to database if it doesn't already exist
        '''
        return self.graph_trav.V().has('application', 'site', site).as_('v') \
                .V().has('topic', 'topic', topic) \
                .coalesce(inE('about').where(outV().as_('v')), addE('about') \
                .from_('v')).next()

    def add_app_property(self, site, prop, value):
        '''
        updates only one of the application's properties
        '''
        return self.graph_trav.V().has('application', 'site', site) \
                .property(Cardinality.set_, prop, value).next()

    def add_annotation(self, site, doi, annotation):
        '''
        adds relationship to database if it doesn't already exist
        '''
        return self.graph_trav.V().has('site', site).outE("uses").where(otherV().has("doi", doi)) \
            .property('annotation', annotation).next()

    def verify_app(self, site, verifier):
        '''
        adds relationship to database if it doesn't already exist
        '''
        return self.graph_trav.V().has('application', 'site', site) \
            .property(Cardinality.single, 'verified', True) \
            .property(Cardinality.single, 'verifier', verifier).next()

    def verify_relationship(self, site, doi, verifier):
        '''
        adds relationship to database if it doesn't already exist
        '''
        return self.graph_trav.V().has('site', site).outE("uses").where(otherV().has("doi", doi)) \
            .property('verified', True) \
            .property('verifier', verifier).next()

    def update_app(self, site, app):
        '''
        updates application vertex in the database with new information
        '''
        self.graph_trav.V().has('application', 'site', site) \
            .sideEffect(__.outE("about").where(otherV().hasLabel("topic")).drop()) \
            .sideEffect(__.properties('type').drop()) \
            .sideEffect(__.properties('essential_variable').drop()) \
            .property(Cardinality.single, 'name', app['name']) \
            .property(Cardinality.single, 'site', app['site']) \
            .property(Cardinality.single, 'screenshot', app['screenshot']) \
            .property(Cardinality.single, 'publication', app['publication']) \
            .property(Cardinality.single, 'description', app['description']) \
            .next()
        for i in range(len(app['topic'])):
            self.connect_topic(app['site'], app['topic'][i])
        for i in range(len(app['type'])):
            self.add_app_property(app['site'], 'type', app['type'][i])
        if 'essential_variable' in app:
            for i in range(len(app['essential_variable'])):
                if app['essential_variable'][i] in essential_variables.values:
                    self.add_app_property(app['site'], 'essential_variable', app['essential_variable'][i])

    def update_app_property(self, site, prop, value):
        '''
        updates only one of the application's properties
        if application property does not exist it will not do anything
        '''
        return self.graph_trav.V().has('application', 'site', site) \
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

    def delete_topic(self, topic):
        '''
        deletes topic vertex in the database
        '''
        return self.graph_trav.V().has('topic', 'topic', topic).drop().iterate()

    def delete_app(self, site):
        '''
        deletes application vertex in the database
        '''
        return self.graph_trav.V().has('application', 'site', site).drop().iterate()

    def delete_dataset(self, doi):
        '''
        deletes dataset vertex in the database
        '''
        return self.graph_trav.V().has('dataset', 'doi', doi).drop().iterate()

    def delete_relationship(self, site, doi):
        '''
        deletes relationship edge in the database
        '''
        return self.graph_trav.V().has('site', site).outE("uses").where(otherV().has("doi", doi)).drop().iterate();
    
    def delete_orphan_datasets(self):
        '''
        deletes all dataset vertexes in the database that have no connections
        '''
        return self.graph_trav.V().hasLabel('dataset').where(bothE().count().is_(0)).drop().iterate()

    def api(self, topics, types, verified=False, incl_truncated_name=False, incl_truncated_description=False):
        '''
        returns all application type nodes that have the provided topics and types
        '''
        info = self.graph_trav.V().hasLabel('application').toList()
        if verified:
            info = self.graph_trav.V(info).has('application', 'verified', True).toList()
        if info and len(topics) != 0:
            info = self.graph_trav.V(info).where(__.outE("about").otherV().has("topic", within(*topics))).toList()
        if info and len(types) != 0:
            info = self.graph_trav.V(info).has('type', within(*types)).toList()
        if not info:
            return info
        app_list = self.graph_trav.V(info).valueMap().toList()
        if incl_truncated_name:
            app_list = list(map(lambda a: a | { 'truncated_name': str_helper.smart_truncate(a['name'][0]) }, app_list))
        if incl_truncated_description:
            app_list = list(map(lambda a: a | { 'truncated_description': str_helper.smart_truncate(a['description'][0], length=300) }, app_list))
        return app_list

    def get_topics_by_types(self, types):
        return self.graph_trav.V().has('type', within(*types)).outE('about').otherV().values('topic').toSet()

    def get_types_by_topics(self, topics):
        return self.graph_trav.V().has('topic', within(*topics)).inE('about').otherV().values('type').toSet()
