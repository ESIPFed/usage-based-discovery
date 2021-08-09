from tests.routes_test import RoutesTest
from tests.resources.mock_data import MockData
from util.env_helper import set_var


class TestRelationshipRoutes(RoutesTest):

    def test_add_rltsp_route_research(self):
        data = MockData.get('Research', "9020-0003-9403-1032")
        with self.flask_app.test_client() as c:
            set_var('ORCID', "9020-0003-9403-1032")
            c.get(self.get_url_for('login'), follow_redirects=True)

            rv = c.post(self.get_url_for('add_relationship'), 
                content_type='multipart/form-data', 
                data=data['form'])
            
            assert rv.status_code == 200

            assert(self.db.get_vertex_count() == 6)
            assert(self.db.get_edge_count() == 5)

            app = self.db.get_app(data['form']['site'])[0]
            ds0 = self.db.get_dataset(data['form']['DOI_1'])[0]
            ds1 = self.db.get_dataset(data['form']['DOI_2'])[0]

            assert(ds0 == data['datasets'][0])
            assert(ds1 == data['datasets'][1])
            assert(app == data['app'])

            rv = c.post(self.get_url_for('add_relationship'), 
                content_type='multipart/form-data', 
                data={
                    'type': 'edit_application',
                    'app_site': data['form']['site']
                })
            
            assert rv.status_code == 200

    def test_add_rltsp_route_research_update(self):
        data = MockData.get('Research', "9020-0003-9403-1032", is_edit=False)
        with self.flask_app.test_client() as c:
            set_var('ORCID', "9020-0003-9403-1032")
            c.get(self.get_url_for('login'), follow_redirects=True)

            rv = c.post(self.get_url_for('add_relationship'), 
                content_type='multipart/form-data', 
                data=data['form'])
            
            assert rv.status_code == 200

            assert(self.db.get_vertex_count() == 6)
            assert(self.db.get_edge_count() == 5)

            app = self.db.get_app(data['form']['site'])[0]
            ds0 = self.db.get_dataset(data['form']['DOI_1'])[0]
            ds1 = self.db.get_dataset(data['form']['DOI_2'])[0]

            assert(ds0 == data['datasets'][0])
            assert(ds1 == data['datasets'][1])
            assert(app == data['app'])

        data = MockData.get('Research', "9020-0003-9403-1032", is_edit=True)
        with self.flask_app.test_client() as c:
            set_var('ORCID', "9020-0003-9403-1032")
            c.get(self.get_url_for('login'), follow_redirects=True)

            rv = c.post(self.get_url_for('add_relationship'), 
                content_type='multipart/form-data', 
                data=data['form'])
            
            assert rv.status_code == 200

            assert(self.db.get_vertex_count() == 6)
            assert(self.db.get_edge_count() == 5)

            app = self.db.get_app(data['form']['site'])[0]
            ds0 = self.db.get_dataset(data['form']['DOI_1'])[0]
            ds1 = self.db.get_dataset(data['form']['DOI_2'])[0]

            assert(ds0 == data['datasets'][0])
            assert(ds1 == data['datasets'][1])
            assert(app == data['app'])

    def test_add_rltsp_route_software(self):
        data = MockData.get('Software', "9020-0003-9403-1032")
        with self.flask_app.test_client() as c:
            set_var('ORCID', "9020-0003-9403-1032")
            c.get(self.get_url_for('login'), follow_redirects=True)

            rv = c.post(self.get_url_for('add_relationship'), 
                content_type='multipart/form-data', 
                data=data['form'])
            
            assert rv.status_code == 200

            assert(self.db.get_vertex_count() == 6)
            assert(self.db.get_edge_count() == 5)

            app = self.db.get_app(data['form']['site'])[0]
            ds0 = self.db.get_dataset(data['form']['DOI_1'])[0]
            ds1 = self.db.get_dataset(data['form']['DOI_2'])[0]

            assert(ds0 == data['datasets'][0])
            assert(ds1 == data['datasets'][1])
            assert(app == data['app'])
            
        

        