import sys
import os
sys.path.append("../util")
from env_loader import env_vars_loaded, load_env

class TestInit():

    def test_env_vars_loaded_empty_dict(self):
        assert not env_vars_loaded({"":""})

    def test_not_env_vars_loaded(self):
        assert not env_vars_loaded({"NEPTUNEDBRO":"xyz"})
    
    def test_env_vars_loaded(self):
        assert env_vars_loaded({
            "NEPTUNEDBRO": "localhost", 
            "STAGE": "/stg",
            "CLIENT_SECRET": "YOUR_CLIENT_SECRET_FOR_ORCID_OAUTH",
            "CLIENT_ID": "YOUR_CLIENT_ID_FOR_ORCID_OAUTH",
            "SECRET_KEY": "secretz",
            "S3_BUCKET": "buket"})
