import os
import secrets


def load_vars(orcid=None, flask_env=None, neptune_endpoint=None):
    """ Load the specified env vars, only if they don't already exist. """
    if ('NEPTUNEDBRO' not in os.environ or not os.environ['NEPTUNEDBRO']) and neptune_endpoint:
        os.environ['NEPTUNEDBRO'] = neptune_endpoint
    
    if ('APP_SECRET_KEY' not in os.environ or not os.environ['APP_SECRET_KEY']):
        os.environ['APP_SECRET_KEY'] = secrets.token_urlsafe(10)
    
    if ('ORCID' not in os.environ or not os.environ['ORCID']) and orcid:
        os.environ['ORCID'] = orcid
    
    if ('FLASK_ENV' not in os.environ or not os.environ['FLASK_ENV']) and flask_env:
        os.environ['FLASK_ENV'] = flask_env

def set_var(k, v):
    os.environ[k] = v

def clear_vars():
    if 'NEPTUNEDBRO' in os.environ:
        del os.environ['NEPTUNEDBRO']
    if 'APP_SECRET_KEY' in os.environ:
        del os.environ['APP_SECRET_KEY']
    if 'ORCID' in os.environ:
        del os.environ['ORCID']
    if 'FLASK_ENV' in os.environ:
        del os.environ['FLASK_ENV']