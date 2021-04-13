import sys
sys.path.append("../")
from util.graph_db import GraphDB, valid_endpoint

SITE = 'https://example.com'
DOI = '1234567890'
TOPIC = 'Test'
CHANGE_SITE = 'Change https://example.com'
CHANGE_DOI = 'Change 1234567890'
CHANGE_TOPIC = 'Change Test'

APP = {
        'site': SITE,
        'topic': [TOPIC],
        'name': 'Testing 123',
        'screenshot': 'Testing 123.jpg',
        'publication': 'None',
        'description': 'example description 123'
}

print(APP)

CHANGE_APP = {
        'site': CHANGE_SITE,
        'topic': ['Change Test'],
        'name': 'Change Testing 123',
        'screenshot': 'Change Testing 123.jpg',
        'publication': 'Change None',
        'description': 'Change example description 123'
}

CHANGE_PROP_APP = {
        'site': CHANGE_SITE,
        'name': 'Change Testing 123',
        'screenshot': 'Change Testing 123.jpg',
        'publication': 'Change None',
        'description': 'summary of usage/application'
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

class TestInit():

    def setup_method(self):
        self.db = GraphDB()

    def teardown_method(self):
        self.db = None

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
        assert path[0] == {'site': ['https://example.com'], 'publication': ['None'], 'name': ['Testing 123'], 'description': ['example description 123'], 'screenshot': ['Testing 123.jpg'], 'discoverer': [''], 'verified': [False], 'verifier': ['']}
        assert path[1] == {'annotation': '', 'verifier': '', 'verified': False, 'discoverer': ''}
        assert path[2] == {'title': ['dataset'], 'doi': ['1234567890']}

    def test_verify_relationship(self):
        self.db.verify_relationship(SITE, DOI, '0000-0000-0000-0000')
        path = self.db.get_dataset_by_app(SITE, DOI)[0]
        print(path)
        assert path[0] == {'site': ['https://example.com'], 'publication': ['None'], 'name': ['Testing 123'], 'description': ['example description 123'], 'screenshot': ['Testing 123.jpg'], 'discoverer': [''], 'verified': [False], 'verifier': ['']}
        assert path[1] == {'annotation': '', 'verifier': '0000-0000-0000-0000', 'verified': True, 'discoverer': ''}
        assert path[2] == {'title': ['dataset'], 'doi': ['1234567890']}

    def test_verify_app(self):
        self.db.verify_app(SITE, '0000-0000-0000-0000')
        app = self.db.get_app(SITE)[0]
        print(app)
        assert app == {'site': ['https://example.com'], 'publication': ['None'], 'name': ['Testing 123'], 'description': ['example description 123'], 'screenshot': ['Testing 123.jpg'], 'discoverer': [''], 'verified': [True], 'verifier': ['0000-0000-0000-0000']}

    def test_update_app(self):
        self.db.add_topic(CHANGE_TOPIC)
        self.db.update_app(SITE, CHANGE_APP)
        app = self.db.mapify(self.db.get_app(CHANGE_SITE))
        CHANGE_APP.pop('topic')
        print(CHANGE_APP, app[0])
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

    def test_clear_database_end(self):
        print(self.db.clear_database())
        assert self.db.get_vertex_count() == 0
        assert self.db.get_edge_count() == 0
