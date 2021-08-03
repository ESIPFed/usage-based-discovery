import os
import secrets

def load_vars(orcid=None, flask_env=None, neptune_endpoint=None):
    if ('NEPTUNEDBRO' not in os.environ or not os.environ['NEPTUNEDBRO']) and neptune_endpoint:
        os.environ['NEPTUNEDBRO'] = neptune_endpoint
    os.environ['APP_SECRET_KEY'] = secrets.token_urlsafe(10)
    print(os.environ['NEPTUNEDBRO'])
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