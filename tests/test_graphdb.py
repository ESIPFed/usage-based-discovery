import pytest
import sys
from argparse import Namespace
sys.path.append("../")
from util import graph_db

def test_parse_options():
	expected = Namespace(ifile='algo-output.csv', neptune=None)
	assert graph_db.parse_options() == expected

def test_connect():
    with pytest.raises(SystemExit) as e:
        graph_db.connect(None)
    assert e.type == SystemExit
    assert e.value.code == "Neptune Endpoint was not supplied in either command line or NEPTUNEDBRO environment"
