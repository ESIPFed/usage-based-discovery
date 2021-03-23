from util.graph_db import GraphDB
from util.s3_functions import s3Functions
from flask import Flask, render_template 

from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

import os
import pprint

app = Flask(__name__)

stage = os.environ.get('STAGE')

# Initial screen
@app.route('/')
def home():
    g = GraphDB()
    topics = g.get_topics()
    return render_template('init.html', stage=stage, topics=topics)

# About page
@app.route('/about')
def about():
    return render_template('about.html', stage=stage)

@app.route('/explore')
def explore():
    g = GraphDB()
    data = g.get_data()
    return render_template('graph.html', stage=stage, data=data)

# Main screen
@app.route('/<topic>/<app>')
def main(topic, app):
    g = GraphDB()
    topics = g.get_topics()
    # query only for application relating to specified topic
    relapps = g.get_apps_by_topic(topic)
    # query for the first application in relapps list
    if(app == 'all'):
        appsel = None
        # query for datasets related to the topic
        datasets = g.get_datasets_by_topic(topic)
        pprint.pprint(datasets)
        filename = relapps[0]['screenshot']
    # query for single application (vertex) with name specified by parameter
    else:
        appsel = g.get_app(app)
        filename = appsel[0]['screenshot']
        # query for all datasets relating to specified application
        datasets = g.get_datasets_by_app(app)
    s3 = s3Functions()
    screenshot = s3.create_presigned_url('test-bucket-parth', filename)
    return render_template('index.html', stage=stage, topic=topic, \
        topics=topics, apps=relapps, app=appsel, datasets=datasets, screenshot=screenshot)

if __name__ == '__main__':
    app.run(debug=True)
