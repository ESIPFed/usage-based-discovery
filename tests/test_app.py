from util.env_helper import load_vars, clear_vars
load_vars(flask_env='development')

from util.graph_db import GraphDB
from app_factory import create_app
from flask import url_for, session

import os

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

    def setup_class(self):
        self.db = GraphDB()

    def setup_method(self):
        clear_vars()
        load_vars(flask_env='development')
        flask_app = create_app()
        flask_app.testing = True
        flask_app.config['SERVER_NAME'] = 'localhost.localdomain'
        self.flask_app = flask_app
        self.db.clear_database()

    def test_base_route(self):
        url = self.get_url_for('topics')
        response = self.flask_app.test_client().get(url)
        # print(response)
        # print(response.data)
        assert response.status_code == 200

    def test_about_route(self):
        url = self.get_url_for('about')
        response= self.flask_app.test_client().get(url)
        assert response.status_code == 200

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

    def test_change_topic_route_forbidden_if_not_supervisor(self):
        url = self.get_url_for('post_change_topic')
        response = self.flask_app.test_client().post(url, content_type='multipart/form-data', 
                                    data={})
        assert response.status_code == 403
        url = self.get_url_for('get_change_topic')
        response = self.flask_app.test_client().post(url)
        assert response.status_code == 403

    def test_change_topic_route_rename(self):
        with self.flask_app.test_client() as c:
            load_vars(flask_env='development', orcid="9020-0003-9403-1032")
            c.get(self.get_url_for('login'), follow_redirects=True)

            self.db.add_topic(TOPIC)
            assert self.db.get_topics() == [TOPIC]
            rv = c.post(self.get_url_for('post_change_topic'), 
                content_type='multipart/form-data', 
                data={
                    'old-name': TOPIC,
                    'new-name': 'a new topic name',
                    'action': 'edit'
                })
            assert rv.status_code == 200
            assert self.db.get_topics() == ['a new topic name']

    def test_change_topic_route_new(self):
        with self.flask_app.test_client() as c:
            load_vars(flask_env='development', orcid="9020-0003-9403-1032")
            c.get(self.get_url_for('login'), follow_redirects=True)

            assert self.db.get_topics() == []
            rv = c.post(self.get_url_for('post_change_topic'), 
                content_type='multipart/form-data', 
                data={
                    'old-name': '',
                    'new-name': 'a new topic name',
                    'action': 'edit'
                })
            assert rv.status_code == 200
            assert self.db.get_topics() == ['a new topic name']

    def test_change_topic_route_delete(self):
        with self.flask_app.test_client() as c:
            load_vars(flask_env='development', orcid="9020-0003-9403-1032")
            c.get(self.get_url_for('login'), follow_redirects=True)

            self.db.add_topic(TOPIC)
            assert self.db.get_topics() == [TOPIC]
            rv = c.post(self.get_url_for('post_change_topic'), 
                content_type='multipart/form-data', 
                data={
                    'old-name': TOPIC,
                    'new-name': '',
                    'action': 'delete'
                })
            assert rv.status_code == 200
            assert self.db.get_topics() == []

        