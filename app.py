from util.graph_db import GraphDB
from util.s3_functions import s3Functions
from flask import Flask, render_template, request
from model import RegForm

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

@app.route('/add-relationship', methods=["GET","POST"])
def add_relationship():
    g = GraphDB()
    topics = g.get_topics()
    status= "none"
    f=None
    if request.method == "POST":
        f = request.form
        status = "success"
        #do checks and determite if submission is valid
        if not validate_form(f):
            status = "failure"
        #return render_template('add-relationship.html', stage=stage, status=status, form=f)
    return render_template('add-relationship.html', stage=stage, status=status, form=f, topics=topics)

def validate_form(f):
    for item in f.values():
        if len(item)==0:
            return False
    return True

if __name__ == '__main__':
    app.run(debug=True)
