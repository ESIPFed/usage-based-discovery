import os

from dotenv import load_dotenv
import app_factory
from util import env_helper

app = None
is_docker = os.environ.get('IS_DOCKER') == 'true'
is_dev = os.environ.get('FLASK_ENV') == 'development'
if not (is_docker or is_dev):
    app = app_factory.create_flask_app()

if __name__ == '__main__':
    # this should only be invoked in non-production modes (FLASK_ENV != production)
    load_dotenv('.env.development')
    neptune_endpoint = 'ws://localhost:8183/gremlin'
    host = None
    if is_docker:
        neptune_endpoint = 'ws://host.docker.internal:8183/gremlin'
        host='0.0.0.0'
    env_helper.load_vars(flask_env='development', neptune_endpoint=neptune_endpoint)
    app = app_factory.create_flask_app()
    
    app.run(debug=True, host=host)