from util.graph_db import GraphDB
from flask import Flask, render_template 

from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

import os

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
    # query for single application (vertex) with name specified by parameter
    else:
        appsel = g.get_app(app)
        # query for all datasets relating to specified application
        datasets = g.get_datasets_by_app(app)
    return render_template('index.html', stage=stage, topic=topic, \
        topics=topics, apps=relapps, app=appsel, datasets=datasets)

if __name__ == '__main__':
    app.run(debug=True)
