try:
    from flask import Flask
    import sys
    sys.path.append("../")
    from util.graph_db import GraphDB
    from app import app as flask_app
    import pytest
except Exception as e:
    print("Some Modules are Missing {} ".format(e))

NAME = 'Testing123'
TOPIC = 'Test'
APP = {
        'topic': [TOPIC],
        'name': NAME,
        'site': 'https://example.com',
        'screenshot': 'Testing 123.jpg',
        'publication': 'None',
        'description': 'example description 123'
}

class TestFlask():

    def setup_method(self):
        self.client = flask_app.test_client()

    def test_base_route(self):
        url = '/'
        response = self.client.get(url)
        print(response)
        print(response.data)
        assert response.status_code == 200

    def test_about_route(self):
        url = '/about'
        response= self.client.get(url)
        assert response.status_code == 200

    def test_app_route(self):
        #add gremlin topic and app
        test_g = GraphDB()
        test_g.add_app(APP)
        url = '/{}/{}'.format(TOPIC,NAME)
        response=self.client.get(url)
        data = str(response.data)
        assert response.status_code == 200
        assert NAME in data
        assert TOPIC in data

    def test_explore_route(self):
        url = 'explore'
        response = self.client.get(url)
        assert response.status_code == 200
        data = str(response.data)
        assert NAME in data
        assert TOPIC in data

    def test_explore_route(self):
        url = 'explore'
        response = self.client.get(url)
        assert response.status_code == 200
        data = str(response.data)
        assert NAME in data
        assert TOPIC in data
