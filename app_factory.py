from flask import Flask
from flask_fontawesome import FontAwesome
import os
from util import secrets_manager
from routes import topic_routes, app_routes, user_routes, error_routes, \
    relationship_routes, info_routes, dataset_routes, before_routes

'''
# app layout
APP = {
    'name': 'test_name',
    'site': 'https://example.com',
    'type': [<type_1>, <type_2>] #multi-property so it returns as a list in value_map graph function
    'screenshot': 'Testing-123.png',
    'publication': 'None' or '<url>',
    'description': 'example description 123',
    'essential_variable': '[Precipitation]'
}

# session layout
Session = {
    'orcid': (String)'9999-9999-9999-9999' (property will not exist if not logged in)
    'role': (String)'supervisor','general' (property will not exist if not logged in)
    'changes': (List)Changes_made, a stack of changes make by a user (like a history) to be used to undo changes 
}

'''

def create_flask_app():
    flask_app = Flask(__name__)
    flask_app.config['JSON_SORT_KEYS'] = False
    FontAwesome(flask_app)

    if os.environ.get('FLASK_ENV') == 'development':
        flask_app.secret_key = os.environ.get('APP_SECRET_KEY')
    else:
        flask_app.secret_key = secrets_manager.get_secret(os.environ.get('APP_SECRET_ARN'))
    
    error_routes.bind(flask_app)    

    before_routes.bind(flask_app)

    user_routes.bind(flask_app)
    
    topic_routes.bind(flask_app)

    app_routes.bind(flask_app)

    dataset_routes.bind(flask_app)

    relationship_routes.bind(flask_app)

    info_routes.bind(flask_app)
    
    return flask_app