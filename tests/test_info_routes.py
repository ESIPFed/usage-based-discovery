from tests.routes_test import RoutesTest
from util.env_helper import load_vars

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

class TestInfoRoutes(RoutesTest):

    def test_explore_route(self):
        self.db.add_topic(TOPIC)
        self.db.add_app(APP, verified=True)
        url = self.get_url_for('explore')
        response = self.flask_app.test_client().get(url)
        assert response.status_code == 200
        data = str(response.data)
        data = response.data.decode("utf-8")
        # print(data)
        self.db.verify_app(SITE, 'temp-orcid')
        assert NAME in data
        assert TOPIC in data

    def test_about_route(self):
        url = self.get_url_for('about')
        response= self.flask_app.test_client().get(url)
        assert response.status_code == 200
