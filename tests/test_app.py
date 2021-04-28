try:
    from flask import Flask
    import sys
    sys.path.append("../")
    from util.graph_db import GraphDB
    from app import app as flask_app
    import pytest
    import urllib
except Exception as e:
    print("Some Modules are Missing {} ".format(e))

NAME = 'Testing123'
SITE = 'https///:example.com'
ENCODED_SITE =  urllib.parse.quote(urllib.parse.quote(SITE, safe=''), safe='') 

TOPIC = 'Test'
TYPE = 'unclassified'
APP = {
        'topic': [TOPIC],
        'type': [TYPE],
        'name': NAME,
        'site': SITE,
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
        test_g.add_topic(TOPIC)
        test_g.add_app(APP, verified=True)
        url = '/{}/{}/{}'.format(TYPE,TOPIC,ENCODED_SITE)
        response=self.client.get(url)
        data = str(response.data)
        print(data)
        assert response.status_code == 200
        assert NAME in data
        assert TOPIC in data
        url = '/{}/{}/{}'.format('all',TOPIC,'all')
        response=self.client.get(url)
        data = str(response.data)
        print(data)
        assert response.status_code == 302 
 
    def test_explore_route(self):
        url = '/explore'
        response = self.client.get(url)
        assert response.status_code == 200
        data = str(response.data)
        data = response.data.decode("utf-8")
        print(data)
        test_g = GraphDB()
        test_g.verify_app(SITE, 'temp-orcid')
        assert NAME in data
        assert TOPIC in data
