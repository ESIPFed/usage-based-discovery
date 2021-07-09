from util.graph_db import GraphDB
from app import create_app
from flask import url_for
from util.env_helper import setup_env

NAME = 'Testing123'
SITE = 'https///:example.com'

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

class TestApp():

    def get_url_for(self, route, **kwargs):
        with self.flask_app.app_context():
            return url_for(route, **dict(kwargs, _external=False))

    def setup_method(self):
        setup_env(flask_env='development')
        flask_app = create_app()
        flask_app.testing = True
        flask_app.config['SERVER_NAME'] = 'localhost.localdomain'
        self.flask_app = flask_app
        self.client = flask_app.test_client()

    def test_base_route(self):
        url = self.get_url_for('topics')
        response = self.client.get(url)
        # print(response)
        # print(response.data)
        assert response.status_code == 200

    def test_about_route(self):
        url = self.get_url_for('about')
        response= self.client.get(url)
        assert response.status_code == 200

    def test_app_route(self):
        #add gremlin topic and app
        test_g = GraphDB()
        test_g.add_topic(TOPIC)
        test_g.add_app(APP, verified=True)
        url = self.get_url_for('apps', string_type=TYPE, string_topic=TOPIC, app_site=SITE)
        response=self.client.get(url)
        data = str(response.data)
        # print(data)
        assert response.status_code == 200
        assert NAME in data
        assert TOPIC in data
        url = self.get_url_for('apps', string_type='all', string_topic=TOPIC, app_site='all')
        response=self.client.get(url)
        data = str(response.data)
        # print(data)
        assert response.status_code == 200 
 
    def test_explore_route(self):
        url = self.get_url_for('explore')
        response = self.client.get(url)
        assert response.status_code == 200
        data = str(response.data)
        data = response.data.decode("utf-8")
        # print(data)
        test_g = GraphDB()
        test_g.verify_app(SITE, 'temp-orcid')
        assert NAME in data
        assert TOPIC in data
