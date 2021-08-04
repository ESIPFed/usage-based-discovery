from tests.routes_test import RoutesTest
from util.env_helper import set_var

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

class TestTopicRoutes(RoutesTest):

    def test_base_route(self):
        url = self.get_url_for('topics')
        response = self.flask_app.test_client().get(url)
        # print(response)
        # print(response.data)
        assert response.status_code == 200

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
            set_var('ORCID', "9020-0003-9403-1032")
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
            set_var('ORCID', "9020-0003-9403-1032")
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
            set_var('ORCID', "9020-0003-9403-1032")
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

    def test_change_topic_route_delete_empty_name(self):
        with self.flask_app.test_client() as c:
            set_var('ORCID', "9020-0003-9403-1032")
            c.get(self.get_url_for('login'), follow_redirects=True)

            self.db.add_topic('')
            assert self.db.get_topics() == ['']
            rv = c.post(self.get_url_for('post_change_topic'), 
                content_type='multipart/form-data', 
                data={
                    'old-name': '',
                    'new-name': '',
                    'action': 'delete'
                })
            assert rv.status_code == 200
            assert self.db.get_topics() == []

    def test_change_topic_route_delete_nonexistent_returns_200(self):
        with self.flask_app.test_client() as c:
            set_var('ORCID', "9020-0003-9403-1032")
            c.get(self.get_url_for('login'), follow_redirects=True)

            self.db.add_topic('Cyclones')
            assert self.db.get_topics() == ['Cyclones']
            rv = c.post(self.get_url_for('post_change_topic'), 
                content_type='multipart/form-data', 
                data={
                    'old-name': '',
                    'new-name': '',
                    'action': 'delete'
                })
            assert rv.status_code == 200
            assert self.db.get_topics() == ['Cyclones']
        

        