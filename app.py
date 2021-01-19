from util import graph_db
from flask import Flask, render_template 

from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

import os

app = Flask(__name__)

# getting the database reader endpoint as an environment variable
dbro = os.environ.get('NEPTUNEDBRO')

# Initial screen
@app.route('/')
def home():
	graph_trav = db_connect(dbro)
    topics = db_get_topics(graph_trav)
	graph_trav.close()
    return render_template('init.html', topics=topics)

# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Main screen 
@app.route('/<topic>/<app>') 
def main(topic, app): 

    # initiate graph connection
	graph_trav= db_connect(dbro)

    # query for all topic property values and put into list
    topics = db_get_topics(graph_trav)
  
    # query only for application relating to specified topic
    relapps = db_get_topic_apps(graph_trav, topic)
    
    # query for the first application in relapps list
    if(app == 'all'):
        appsel = None

        # query for datasets related to the topic
		datasets = db_get_topic_datasets(graph_trav, topic)

    # query for single application (vertex) with name specified by parameter
    else:
        appsel = g.V().has('application', 'name', app).elementMap().toList()
        
        # query for all datasets relating to specified application
   		datasets = db_get_app_datasets(graph_trav, app)

    # close connection
    remoteConn.close()
    return render_template('index.html', topic=topic, \
        topics=topics, apps=relapps, app=appsel, datasets=datasets)


if __name__ == '__main__':
    app.run(debug=True)

