from tests.routes_test import RoutesTest
from util.env_helper import load_vars, set_var

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

class TestAppRoutes(RoutesTest):

    def test_app_route(self):
        #add gremlin topic and app
        self.db.add_topic(TOPIC)
        self.db.add_app(APP, verified=True)
        url = self.get_url_for('apps', string_type=TYPE, string_topic=TOPIC, app_site=SITE)
        response = self.flask_app.test_client().get(url)
        data = str(response.data)
        # print(data)
        assert response.status_code == 200
        assert NAME in data
        assert TOPIC in data
        url = self.get_url_for('apps', string_type='all', string_topic=TOPIC, app_site='all')
        response = self.flask_app.test_client().get(url)
        data = str(response.data)
        # print(data)
        assert response.status_code == 200

    def test_apps_download_route(self):
        #add gremlin topic and app
        self.db.add_topic(TOPIC)
        self.db.add_app(APP, verified=True)
        self.db.add_dataset({'doi': 'data doi', 'title': 'dataset titel'})
        self.db.add_relationship(SITE, 'data doi')
        with self.flask_app.test_client() as c:
            set_var('ORCID', "9020-0003-9403-1032")
            c.get(self.get_url_for('login'), follow_redirects=True)
            rv = c.get(self.get_url_for('download_apps'))
            data = str(rv.data)
            assert rv.status_code == 200
            assert NAME in data
            assert TOPIC in data
            csv_data = 'https///:example.com,Testing 123.jpg,example description 123,None,,True,,data doi,dataset titel,,,False,'
            assert csv_data in data
            
        
