from util import env_helper
env_helper.load_vars(flask_env='development')

import app_factory

if __name__ == '__main__':
    app = app_factory.create_flask_app()
    
    # runs app and loads .env if it exists
    # load_dotenv=True will not override any env vars
    app.run(debug=True, load_dotenv=True)