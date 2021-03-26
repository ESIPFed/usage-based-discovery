import sys
sys.path.append("../util")
from graph_db import GraphDB, valid_endpoint

NAME = 'Testing 123'
DOI = '1234567890'
CHANGE_NAME = 'Change Testing 123'
CHANGE_DOI = 'Change 1234567890'

APP = {
        'topic': 'Test',
        'name': NAME,
        'site': 'https://example.com',
        'screenshot': 'Testing 123.jpg',
        'publication': 'None',
        'description': 'example description 123'
}

CHANGE_APP = {
        'topic': 'Change Test',
        'name': CHANGE_NAME,
        'site': 'Change https://example.com',
        'screenshot': 'Change Testing 123.jpg',
        'publication': 'Change None',
        'description': 'Change example description 123'
}

CHANGE_PROP_APP = {
        'topic': 'Fires',
        'name': CHANGE_NAME,
        'site': 'Change https://example.com',
        'screenshot': 'Change Testing 123.jpg',
        'publication': 'Change None',
        'description': 'Change example description 123'
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
        assert not self.db.has_app(NAME)

    def test_add_app(self):
        print(self.db.add_app(APP))
        assert self.db.has_app(NAME)

    def test_add_app_dupe(self):
        startnum = self.db.get_vertex_count()
        self.db.add_app(APP)
        endnum = self.db.get_vertex_count()
        print(startnum, endnum)
        assert startnum == endnum

    def test_has_dataset(self):
        assert not self.db.has_dataset(DOI)

    def test_add_dataset(self):
        print(self.db.add_dataset(DATASET))
        assert self.db.has_dataset(DOI)

    def test_add_dataset_dupe(self):
        startnum = self.db.get_vertex_count()
        self.db.add_dataset(DATASET)
        endnum = self.db.get_vertex_count()
        print(startnum, endnum)
        assert startnum == endnum

    def test_has_relationship(self):
        assert not self.db.has_relationship(NAME, DOI)

    def test_add_relationship(self):
        print(self.db.add_relationship(NAME, DOI))
        assert self.db.has_relationship(NAME, DOI)

    def test_add_relationship_dupe(self):
        startnum = self.db.get_edge_count()
        self.db.add_relationship(NAME, DOI)
        endnum = self.db.get_edge_count()
        print(startnum, endnum)
        assert startnum == endnum

    def test_update_app(self):
        print(self.db.update_app(NAME, CHANGE_APP))
        app = self.db.get_app(CHANGE_NAME)
        assert CHANGE_APP.items() <= app[0].items()

    def test_update_app_property(self):
        print(self.db.update_app_property(CHANGE_NAME, 'topic', 'Fires'))
        app = self.db.get_app(CHANGE_NAME)
        print(CHANGE_PROP_APP.items(), app[0].items())
        assert CHANGE_PROP_APP.items() <= app[0].items()

    def test_add_app_property(self):
        prop = 'query'
        print(self.db.add_app_property(CHANGE_NAME, prop, 'earthdatasearch query here'))
        app = self.db.get_app(CHANGE_NAME)
        print(app[0])
        assert prop in app[0]
        assert 'invalid' not in app[0]
    
    def test_update_dataset(self):
        print(self.db.update_dataset(DOI, CHANGE_DATASET))
        dataset = self.db.get_dataset(CHANGE_DOI)
        print(CHANGE_DATASET.items())
        print(dataset.items())
        assert CHANGE_DATASET.items() <= dataset.items()

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
        print(self.db.delete_relationship(CHANGE_NAME, CHANGE_DOI))
        assert self.db.has_app(CHANGE_NAME)
        assert self.db.has_dataset(CHANGE_DOI)
        assert self.db.get_edge_count() == 0

    def test_delete_app(self):
        print(self.db.add_app(APP))
        print(self.db.delete_app(NAME))
        assert not self.db.has_app(NAME)
        assert self.db.has_app(CHANGE_NAME)

    def test_delete_dataset(self):
        print(self.db.add_dataset(DATASET))
        print(self.db.delete_dataset(DOI))
        assert not self.db.has_dataset(DOI)
        assert self.db.has_dataset(CHANGE_DOI)

    def test_delete_orphan_datasets(self):
        self.db.add_app(CHANGE_APP)
        self.db.add_dataset(CHANGE_DATASET)
        self.db.add_relationship(CHANGE_NAME, CHANGE_DOI)
        self.db.add_dataset(DATASET)
        self.db.delete_orphan_datasets()
        assert not self.db.has_dataset(DOI)
        assert self.db.has_dataset(CHANGE_DOI)

    def test_clear_database_end(self):
        print(self.db.clear_database())
        assert self.db.get_vertex_count() == 0
        assert self.db.get_edge_count() == 0
