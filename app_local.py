from util import env_helper
env_helper.setup_env(flask_env='development')

import app_factory

if __name__ == '__main__':
    app = app_factory.create_app()
    app.run(debug=True)