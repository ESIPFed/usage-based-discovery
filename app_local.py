from util import env_helper
import app_factory

if __name__ == '__main__':
    env_helper.load_vars(flask_env='development', neptune_endpoint='ws://localhost:8182/gremlin')
    app = app_factory.create_flask_app()
    
    # runs app and loads .env if it exists
    # load_dotenv=True will not override any env vars
    app.run(debug=True, load_dotenv=True)