from util.env_helper import load_vars, clear_vars
from util.graph_db import GraphDB
from app_factory import create_flask_app
from flask import url_for

class RoutesTest():

    def get_url_for(self, route, **kwargs):
        with self.flask_app.app_context():
            return url_for(route, **dict(kwargs, _external=False))

    def setup_class(self):
        clear_vars()
        load_vars(flask_env='development', neptune_endpoint='ws://localhost:8183/gremlin')
        self.db = GraphDB()

    def setup_method(self):
        clear_vars()
        load_vars(flask_env='development', neptune_endpoint='ws://localhost:8183/gremlin')
        flask_app = create_flask_app()
        flask_app.testing = True
        flask_app.config['SERVER_NAME'] = 'localhost.localdomain'
        self.flask_app = flask_app
        self.db.clear_database()