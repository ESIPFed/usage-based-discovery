from unittest import mock
import pytest
import sys
sys.path.append("../util")
from graph_db import GraphDB

class TestInit():
    
    def setup_method(self):
        self.db = GraphDB()

    def teardown_method(self):
        self.db = None

    def test_valid_endpoint(self):
        assert self.db.valid_endpoint("wss://endpoint:8182/gremlin") == True
    
    def test_invalid_endpoint_start(self):
        assert self.db.valid_endpoint("endpoint:8182/gremlin") == False
    
    def test_invalid_endpoint_end(self):
        assert self.db.valid_endpoint("wss://endpoint") == False

    def test_clear_database_start(self):
        self.db.clear_database()
        assert self.db.get_vertex_count() == 0

    def test_has_app(self):
        assert self.db.has_app("Testing 123") == False

    def test_add_app(self):
        app = {'topic': 'Test', 'name': 'Testing 123', 'site': 'https://example.com', 'screenshot': 'Testing 123.jpg', 'publication': 'None', 'description': 'example description 123' }
        self.db.add_app(app)
        assert self.db.has_app('Testing 123') == True
    
    def test_has_dataset(self):
        assert self.db.has_dataset('1234567890') == False

    def test_add_dataset(self):
        dataset = {'title': 'dataset', 'doi': '1234567890'}
        self.db.add_dataset(dataset)
        assert self.db.has_dataset('1234567890') == True

    def test_has_relationship(self):
        assert self.db.has_relationship('Testing 123', '1234567890') == False

    def test_add_relationship(self):
        self.db.add_relationship('Testing 123', '1234567890')
        assert self.db.has_relationship('Testing 123', "1234567890") == True

    def test_do_not_add_dupe(self):
        startnum = self.db.get_vertex_count()
        app = {'topic': 'Test', 'name': 'Testing 123', 'site': 'https://example.com', 'screenshot': 'Testing 123.jpg', 'publication': 'None', 'description': 'example description 123' }
        self.db.add_app(app)
        endnum = self.db.get_vertex_count()
        assert startnum == endnum

    def test_clear_database_end(self):
        self.db.clear_database()
        assert self.db.get_vertex_count() == 0





