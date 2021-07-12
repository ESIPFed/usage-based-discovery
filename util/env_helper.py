import os
import secrets

def load_vars(orcid=None, flask_env=None):
    os.environ['NEPTUNEDBRO'] = 'ws://localhost:8182/gremlin'
    os.environ['APP_SECRET_KEY'] = secrets.token_urlsafe(10)

    if orcid:
        os.environ['ORCID'] = orcid
    
    if flask_env:
        os.environ['FLASK_ENV'] = flask_env

def clear_vars():
    if 'NEPTUNEDBRO' in os.environ:
        del os.environ['NEPTUNEDBRO']
    if 'APP_SECRET_KEY' in os.environ:
        del os.environ['APP_SECRET_KEY']
    if 'ORCID' in os.environ:
        del os.environ['ORCID']
    if 'FLASK_ENV' in os.environ:
        del os.environ['FLASK_ENV']