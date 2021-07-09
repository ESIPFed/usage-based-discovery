import os

def setup_env(orcid=None, flask_env=None):
    
    os.environ['NEPTUNEDBRO'] = 'ws://localhost:8182/gremlin'
    os.environ['APP_SECRET_KEY'] = 'not-a-secret'
    
    if orcid:
        os.environ['ORCID'] = orcid
    
    if flask_env:
        os.environ['FLASK_ENV'] = flask_env