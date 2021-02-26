from util.graph_db import GraphDB
from util.s3_functions import s3Functions
from flask import Flask, render_template, request, session, redirect
#from model import RegForm
import requests
import orcid

from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

import os
import subprocess

app = Flask(__name__)

stage = os.environ.get('STAGE')
client_secret = os.environ.get('CLIENT_SECRET')
client_id = os.environ.get('CLIENT_ID')
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
    in_session = "False"
    if 'orcid' in session:
        in_session="True"
    return render_template('index.html', stage=stage, topic=topic, \
        topics=topics, apps=relapps, app=appsel, datasets=datasets, screenshot=screenshot, in_session=in_session)

@app.route('/login')
def login():
    
    code = request.args.get('code')
    '''
    headers = {
        'Accept': 'application/json',
        'Access-Control-Allow-Orgin':'*',
    }

    data = {
      'client_id': client_id,
      'client_secret': client_secret,
      'grant_type': 'authorization_code',
      'code': code,
      'redirect_uri': 'https://p1of926o5h.execute-api.us-west-1.amazonaws.com/dev/login',
    }

    response = requests.get('https://sandbox.orcid.org/oauth/token', headers=headers, data=data, timeout=None)
    '''
    output = subprocess.run(["curl -i -L -H 'Accept: application/json' --data 'client_id=APP-674MCQQR985VZZQ2&client_secret=d08b711e-9411-788d-a474-46efd3956652&grant_type=authorization_code&code=*WkiYjn*' 'https://sandbox.orcid.org/oauth/token'"],check=True, stdout=subprocess.PIPE, universal_newlines=True)
    #api = orcid.PublicAPI(client_id, client_secret, sandbox=True)
    #response = api.get_token_from_authorization_code(code, "https://p1of926o5h.execute-api.us-west-1.amazonaws.com/dev/login")
    print('\n\n This is to TESTTTTTSSSSSTTTT \n')
    print(response.text)
    session['orcid']=response.orcid
    return redirect('/')

@app.route('/auth')
def auth():
    return redirect("https://sandbox.orcid.org/oauth/authorize?client_id={}&response_type=code&scope=/authenticate&redirect_uri=https://p1of926o5h.execute-api.us-west-1.amazonaws.com/dev/login".format(client_id))

@app.route('/add-relationship', methods=["GET","POST"])
def add_relationship():
    g = GraphDB()
    topics = g.get_topics()
    status= "none"
    f=None
    orcid_data= " "
    code = " "
    if request.args.get('code')!=None:
        code = request.args.get('code')
    Trusted= {
                "0000-0002-3675-5603":"Parth Darji",
            }
    
    if request.method == "POST":
        f = request.form
        status = "failure"
        #do checks and determite if submission is valid
        if validate_form(f):
            status = "success"
        
        headers = {
                'Accept': 'application/json',
                }
        data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'authorization_code',
                'code': '*'+code+'*',
                } 
        orcid_data = requests.post('https://sandbox.orcid.org/oauth/token', headers=headers,data=data)
#    orcid= orcid_data.orcid
#            if orcid in Trusted:

    #check if user is authorized by the code in url 
    #if so then we curl with the code and get their orchid id, and if their orchid id is one of the following then we're good
        
    return render_template('add-relationship.html', stage=stage, status=status, form=f, topics=topics, orcid=code)

def validate_form(f):
    for item in f.values():
        if len(item)==0:
            return False
    return True

if __name__ == '__main__':
    app.run(debug=True)
