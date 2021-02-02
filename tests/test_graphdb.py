import sys
sys.path.append("../util")
from graph_db import GraphDB, valid_endpoint

APP = {'topic': 'Test', 'name': 'Testing 123', 'site': 'https://example.com', 'screenshot': 'Testing 123.jpg', 'publication': 'None', 'description': 'example description 123' }

CHANGE_APP = {'topic': 'Change Test', 'name': 'Change Testing 123', 'site': 'Change https://example.com', 'screenshot': 'Change Testing 123.jpg', 'publication': 'Change None', 'description': 'Change example description 123' }

DATASET = {'title': 'dataset', 'doi': '1234567890'}

CHANGE_DATASET = {'title': 'Change dataset', 'doi': 'Change 1234567890'}

def test_valid_endpoint():
    assert valid_endpoint("wss://endpoint:8182/gremlin")

def test_invalid_endpoint_start():
    assert not valid_endpoint("endpoint:8182/gremlin")

def test_invalid_endpoint_end():
    assert not valid_endpoint("wss://endpoint")

class TestInit():
    
    def setup_method(self):
        self.db = GraphDB()

    def teardown_method(self):
        self.db = None

    def test_clear_database_start(self):
        self.db.clear_database()
        assert self.db.get_vertex_count() == 0
        assert self.db.get_edge_count() == 0

    def test_has_app(self):
        assert not self.db.has_app("Testing 123")

    def test_add_app(self):
        self.db.add_app(APP)
        assert self.db.has_app('Testing 123')
 
    def test_add_app_dupe(self):
        startnum = self.db.get_vertex_count()
        self.db.add_app(APP)
        endnum = self.db.get_vertex_count()
        assert startnum == endnum
   
    def test_has_dataset(self):
        assert not self.db.has_dataset('1234567890')

    def test_add_dataset(self):
        self.db.add_dataset(DATASET)
        assert self.db.has_dataset('1234567890')

    def test_add_dataset_dupe(self):
        startnum = self.db.get_vertex_count()
        self.db.add_dataset(DATASET)
        endnum = self.db.get_vertex_count()
        assert startnum == endnum

    def test_has_relationship(self):
        assert not self.db.has_relationship('Testing 123', '1234567890')

    def test_add_relationship(self):
        self.db.add_relationship('Testing 123', '1234567890')
        assert self.db.has_relationship('Testing 123', "1234567890")

    def test_add_relationship_dupe(self):
        startnum = self.db.get_edge_count()
        self.db.add_relationship('Testing 123', '1234567890')
        endnum = self.db.get_edge_count()
        assert startnum == endnum

    def test_update_app(self):
        startapp = self.db.get_app('Testing 123')
        self.db.update_app('Testing 123', CHANGE_APP)
        endapp = self.db.get_app('Change Testing 123')
        assert CHANGE_APP.items() <= endapp[0].items()

    def test_update_dataset(self):
        startdataset = self.db.get_dataset('1234567890')
        self.db.update_dataset('1234567890', CHANGE_DATASET)
        enddataset = self.db.get_dataset('Change 1234567890')
        assert CHANGE_DATASET.items() <= enddataset[0].items()

    def test_delete_application(self):
        self.db.add_app(APP)
        print(self.db.delete_application("Testing 123"))
        assert not self.db.has_app("Testing 123")
        assert self.db.has_app("Change Testing 123")

    def test_delete_dataset(self):
        self.db.add_dataset(DATASET)
        print(self.db.delete_dataset("1234567890"))
        assert not self.db.has_dataset("1234567890")
        assert self.db.has_dataset("Change 1234567890")

    def test_clear_database_end(self):
        self.db.clear_database()
        assert self.db.get_vertex_count() == 0
        assert self.db.get_edge_count() == 0
