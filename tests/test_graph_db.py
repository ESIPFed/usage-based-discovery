from util.graph_db import GraphDB, valid_endpoint
from util.env_helper import load_vars

SITE = 'https://example.com'
DOI = '1234567890'
TOPIC = 'Test'
CHANGE_SITE = 'Change https://example.com'
CHANGE_DOI = 'Change 1234567890'
CHANGE_TOPIC = 'Change Test'

APP = {
        'site': SITE,
        'type': ['Unclassified'],
        'topic': [TOPIC],
        'name': 'Testing 123',
        'screenshot': 'Testing 123.jpg',
        'publication': 'None',
        'description': 'example description 123',
        'essential_variable': ["Carbon Dioxide","Methane","Invalid Variable"]
}

CHANGE_APP = {
        'site': CHANGE_SITE,
        'type': ['Change Unclassified'],
        'topic': [CHANGE_TOPIC],
        'name': 'Change Testing 123',
        'screenshot': 'Change Testing 123.jpg',
        'publication': 'Change None',
        'description': 'Change example description 123',
        'essential_variable': ["Carbon Dioxide","Greenhouse Gases"]
}

CHANGE_PROP_APP = {
        'type': ['Change Unclassified'],
        'site': CHANGE_SITE,
        'name': 'Change Testing 123',
        'screenshot': 'Change Testing 123.jpg',
        'publication': 'Change None',
        'description': 'summary of usage/application',
        'essential_variable': ["Carbon Dioxide","Greenhouse Gases"]
}

DATASET = {'title': 'dataset', 'doi': DOI}

CHANGE_DATASET = {'title': 'Change dataset', 'doi': CHANGE_DOI}

def test_valid_endpoint():
    assert valid_endpoint("wss://endpoint:8182/gremlin")

def test_invalid_endpoint():
    assert not valid_endpoint("")
    assert not valid_endpoint("endpoint")
    assert not valid_endpoint("wss://endpoint")
    assert not valid_endpoint("endpoint:8182/gremlin")

class TestGraphDB():

    def setup_class(self):
        load_vars(flask_env='development', neptune_endpoint='ws://localhost:8182/gremlin')
        self.db = GraphDB()

    def setup_method(self):
        pass

    def test_clear_database_start(self):
        print(self.db.clear_database())
        assert self.db.get_vertex_count() == 0
        assert self.db.get_edge_count() == 0

    def test_has_app(self):
        assert not self.db.has_app("should not exist")

    def test_has_dataset(self):
        assert not self.db.has_dataset("should not exist")

    def test_get_topics(self):
        assert self.db.get_topics() == []

    def test_add_topic(self):
        self.db.add_topic(TOPIC)
        assert self.db.get_topics() == [TOPIC]
        #shouldn't add a duplicate
        startnum = self.db.get_vertex_count()
        self.db.add_topic(TOPIC)
        endnum = self.db.get_vertex_count()
        assert startnum == endnum

    def test_rename_topic(self):
        self.db.add_topic('Fires')
        assert sorted(self.db.get_topics()) == sorted([TOPIC, 'Fires'])
        self.db.rename_topic('Fires', 'Water')
        assert sorted(self.db.get_topics()) == sorted([TOPIC, 'Water'])

    def test_add_app(self):
        self.db.add_app(APP)
        assert self.db.has_app(SITE)
        assert self.db.get_app_topics(SITE) == [TOPIC]
        #shouldn't add a duplicate
        startnum = self.db.get_vertex_count()
        self.db.add_app(APP)
        endnum = self.db.get_vertex_count()
        assert startnum == endnum

    def test_add_dataset(self):
        self.db.add_dataset(DATASET)
        assert self.db.has_dataset(DOI)
        #shouldn't add a duplicate
        startnum = self.db.get_vertex_count()
        self.db.add_dataset(DATASET)
        endnum = self.db.get_vertex_count()
        assert startnum == endnum

    def test_has_relationship(self):
        assert not self.db.has_relationship(SITE, DOI)

    def test_add_relationship(self):
        self.db.add_relationship(SITE, DOI)
        assert self.db.has_relationship(SITE, DOI)
        #shouldn't add a duplicate
        startnum = self.db.get_edge_count()
        self.db.add_relationship(SITE, DOI)
        endnum = self.db.get_edge_count()
        assert startnum == endnum

    def test_get_dataset_by_app(self):
        path = self.db.get_dataset_by_app(SITE, DOI)[0]
        print(path)
        assert path[0] == {'site': ['https://example.com'], 'type': ['Unclassified'], 'publication': ['None'], 'name': ['Testing 123'], 
            'description': ['example description 123'], 'screenshot': ['Testing 123.jpg'], 'discoverer': [''], 'verified': [False], 
            'verifier': [''], 'essential_variable': ["Carbon Dioxide","Methane"]}
        assert path[1] == {'annotation': '', 'verifier': '', 'verified': False, 'discoverer': ''}
        assert path[2] == {'title': ['dataset'], 'doi': ['1234567890']}

    def test_verify_relationship(self):
        self.db.verify_relationship(SITE, DOI, '0000-0000-0000-0000')
        path = self.db.get_dataset_by_app(SITE, DOI)[0]
        print(path)
        assert path[0] == {'site': ['https://example.com'], 'type': ['Unclassified'], 'publication': ['None'], 'name': ['Testing 123'], 
            'description': ['example description 123'], 'screenshot': ['Testing 123.jpg'], 'discoverer': [''], 'verified': [False], 
            'verifier': [''], 'essential_variable': ["Carbon Dioxide","Methane"]}
        assert path[1] == {'annotation': '', 'verifier': '0000-0000-0000-0000', 'verified': True, 'discoverer': ''}
        assert path[2] == {'title': ['dataset'], 'doi': ['1234567890']}

    def test_verify_app(self):
        self.db.verify_app(SITE, '0000-0000-0000-0000')
        app = self.db.get_app(SITE)[0]
        print(app)
        assert app == {'site': ['https://example.com'], 'type': ['Unclassified'], 'publication': ['None'], 'name': ['Testing 123'], 
            'description': ['example description 123'], 'screenshot': ['Testing 123.jpg'], 'discoverer': [''], 'verified': [True], 
            'verifier': ['0000-0000-0000-0000'], 'essential_variable': ["Carbon Dioxide","Methane"]}

    def test_update_app(self):
        self.db.add_topic(CHANGE_TOPIC)
        self.db.update_app(SITE, CHANGE_APP)
        app = self.db.mapify(self.db.get_app(CHANGE_SITE))
        CHANGE_APP.pop('topic')
        print(CHANGE_APP, app[0])
        assert(app[0]['essential_variable'] == CHANGE_APP['essential_variable'])
        assert CHANGE_APP.items() <= app[0].items()

    def test_update_app_property(self):
        print(self.db.update_app_property(CHANGE_SITE, 'description', 'summary of usage/application'))
        app = self.db.mapify(self.db.get_app(CHANGE_SITE))
        print(CHANGE_PROP_APP, app[0])
        assert CHANGE_PROP_APP.items() <= app[0].items()

    def test_add_app_property(self):
        prop = 'query'
        print(self.db.add_app_property(CHANGE_SITE, prop, 'earthdatasearch query here'))
        app = self.db.get_app(CHANGE_SITE)
        print(app[0])
        assert prop in app[0]
        assert 'invalid' not in app[0]
    
    def test_update_dataset(self):
        print(self.db.update_dataset(DOI, CHANGE_DATASET))
        dataset = self.db.mapify(self.db.get_dataset(CHANGE_DOI))
        print(CHANGE_DATASET, dataset)
        assert CHANGE_DATASET.items() <= dataset[0].items()

    def test_get_data(self):
        data = self.db.get_data()
        print(data)
        assert 'nodes' in data
        assert 'links' in data
        assert 'id' in data['nodes'][0]
        assert 'id' in data['links'][0]
        assert 'source' in data['links'][0]
        assert 'target' in data['links'][0]

    def test_delete_relationship(self):
        startnum = self.db.get_edge_count()
        print(self.db.delete_relationship(CHANGE_SITE, CHANGE_DOI))
        assert self.db.has_app(CHANGE_SITE)
        assert self.db.has_dataset(CHANGE_DOI)
        assert self.db.get_edge_count() == startnum-1

    def test_delete_app(self):
        print(self.db.add_app(APP))
        print(self.db.delete_app(SITE))
        assert not self.db.has_app(SITE)
        assert self.db.has_app(CHANGE_SITE)

    def test_delete_dataset(self):
        print(self.db.add_dataset(DATASET))
        print(self.db.delete_dataset(DOI))
        assert not self.db.has_dataset(DOI)
        assert self.db.has_dataset(CHANGE_DOI)

    def test_delete_orphan_datasets(self):
        CHANGE_APP['topic'] = [CHANGE_TOPIC]
        self.db.add_app(CHANGE_APP)
        self.db.add_dataset(CHANGE_DATASET)
        self.db.add_relationship(CHANGE_SITE, CHANGE_DOI)
        self.db.add_dataset(DATASET)
        self.db.delete_orphan_datasets()
        assert not self.db.has_dataset(DOI)
        assert self.db.has_dataset(CHANGE_DOI)

    def test_api(self):
        APPA = {
            'site': 'siteA',
            'type': ['Unclassified'],
            'topic': ['Fire', 'Water'],
            'name': 'Testing 123',
            'screenshot': 'Testing 123.jpg',
            'publication': 'None',
            'description': 'example description 123'
        }
        APPB = {
            'site': 'siteB',
            'type': ['Software'],
            'topic': ['Water'],
            'name': 'Testing 123',
            'screenshot': 'Testing 123.jpg',
            'publication': 'None',
            'description': 'example description 123'
        }
        APPC = {
            'site': 'siteC',
            'type': ['Unclassified', 'Software'],
            'topic': ['Fire'],
            'name': 'Testing 123',
            'screenshot': 'Testing 123.jpg',
            'publication': 'None',
            'description': 'example description 123'
        }
        print(self.db.clear_database())
        self.db.add_topic('Fire')
        self.db.add_topic('Water')
        self.db.add_app(APPA)
        self.db.add_app(APPB)
        self.db.add_app(APPC)
        siteA = self.db.get_app('siteA')[0]
        siteB = self.db.get_app('siteB')[0]
        siteC = self.db.get_app('siteC')[0]
        
        result = self.db.api(['Fire'],['Unclassified'],False)
        assert len(result) == 2
        assert siteA in result and siteB not in result and siteC in result
        result = self.db.api(['Water'],['Unclassified'],False)
        assert len(result) == 1
        assert siteA in result and siteB not in result and siteC not in result
        result = self.db.api([],[],False)
        assert len(result) == 3
        assert siteA in result and siteB in result and siteC in result
        result = self.db.api([],[],True)
        assert len(result) == 0
        assert siteA not in result and siteB not in result and siteC not in result
         
        self.db.verify_app('siteA', '0000-0000-0000-0000')
        siteA = self.db.get_app('siteA')[0]
        result = self.db.api([],[],True)
        assert len(result) == 1
        assert siteA in result and siteB not in result and siteC not in result
        self.db.verify_app('siteB', '0000-0000-0000-0000')
        siteB = self.db.get_app('siteB')[0]
        result = self.db.api([],[],True)
        assert len(result) == 2
        assert siteA in result and siteB in result and siteC not in result
        self.db.verify_app('siteC', '0000-0000-0000-0000')
        siteC = self.db.get_app('siteC')[0]
        result = self.db.api([],[],True)
        assert len(result) == 3
        assert siteA in result and siteB in result and siteC in result
        
        result = self.db.api(['Fire'],['Unclassified'],True)
        assert len(result) == 2
        assert siteA in result and siteB not in result and siteC in result
        result = self.db.api(['Water'],['Unclassified'],True)
        assert len(result) == 1
        assert siteA in result and siteB not in result and siteC not in result

    def test_delete_topic(self):
        self.db.add_app({
            'type': '',
            'topic': ['Fire'],
            'name': 'samplename2',
            'site': 'https://example2.com',
            'screenshot': 'image2.png',
            'publication': 'publication2',
            'description': 'sample description for a sample app2',
            'essential_variable': ['Precipitation']
        })
        self.db.add_dataset({
            'doi': 'datadoi',
            'title': 'samplename'
        })
        self.db.add_relationship('https://example2.com', 'datadoi')

        old_num_vertices = self.db.get_vertex_count()
        old_num_edges = self.db.get_edge_count()
        self.db.delete_topic('Fire')
        assert(self.db.get_topics() == ['Water'])
        assert((old_num_vertices - 1) == self.db.get_vertex_count())
        assert((old_num_edges - 3) == self.db.get_edge_count())

    def test_clear_database_end(self):
        print(self.db.clear_database())
        assert self.db.get_vertex_count() == 0
        assert self.db.get_edge_count() == 0
