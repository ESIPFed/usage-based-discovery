import os
import json
from pathlib import Path

def env_vars_loaded(env_var_names):
    return 'NEPTUNEDBRO' in env_var_names \
        and "STAGE" in env_var_names \
        and "CLIENT_SECRET" in env_var_names \
        and "CLIENT_ID" in env_var_names \
        and "S3_BUCKET" in env_var_names \
        and "SECRET_KEY" in env_var_names

def load_env():
    # if not already loaded via Zappa, load zappa env variables
    zappa_settings_path = Path(__file__).parent / "../zappa_settings.json"
    zappa_file_exists = os.path.isfile(zappa_settings_path)
    if not env_vars_loaded(os.environ.keys()) and zappa_file_exists:
        env_dict = json.load(open(zappa_settings_path))
        for k, v in env_dict.items():
            env_vars = v['environment_variables']
            for k, v in env_vars.items():
                os.environ[k] = v
    # then load local env variables
    os.environ['NEPTUNEDBRO'] = "ws://localhost:8182/gremlin"
    os.environ['STAGE'] = ""
    if env_vars_loaded(os.environ.keys()):
        print('Loaded local env variables')
