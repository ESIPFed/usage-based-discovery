from util.graph_db import GraphDB
from util.s3_functions import s3Functions
from flask import Flask, render_template, request, session, redirect
#from model import RegForm
import requests
import orcid
import json

from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

import os
import subprocess

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY')
stage = os.environ.get('STAGE')
client_secret = os.environ.get('CLIENT_SECRET')
client_id = os.environ.get('CLIENT_ID')
trusted= {
            '0000-0002-3675-5603':'Parth Darji',
        }
'''
g= GraphDB()
APP = {
        'topic': 'Test',
        'name': 'test_name',
        'site': 'https://example.com',
        'screenshot': 'Testing 123.jpg',
        'publication': 'None',
        'description': 'example description 123'
}
g.add_app(app)
topics = g.get_topics()
'''
# Initial screen
@app.route('/')
def home():
    g = GraphDB()
    topics = g.get_topics()
    in_session=False
    if 'orcid' in session:
        in_session=True
    return render_template('init.html', stage=stage, topics=topics, in_session=in_session)

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
        filename = relapps[0]['screenshot']
    # query for single application (vertex) with name specified by parameter
    else:
        appsel = g.get_app(app)
        filename = appsel[0]['screenshot']
        # query for all datasets relating to specified application
        datasets = g.get_datasets_by_app(app)
    s3 = s3Functions()
    screenshot = s3.create_presigned_url('test-bucket-parth', filename)
    in_session = False
    trusted_user = False
    if 'orcid' in session:
        in_session=True
        if session['orcid'] in trusted:
            trusted_user = True
    return render_template('index.html', stage=stage, topic=topic, \
        topics=topics, apps=relapps, app=appsel, datasets=datasets, screenshot=screenshot, in_session=in_session, trusted_user=trusted_user)

@app.route('/login')
def login():

    code = request.args.get('code')
    ''' 
    headers = {
        'Accept': 'application/json',
        'Content-Type':'application/json;charset=UTF-8'
    }

    data = {
      'client_id': client_id,
      'client_secret': client_secret,
      'grant_type': 'authorization_code',
      'code': code,
    }
    print(data)
    url = 'https://sandbox.orcid.org/oauth/token'
    output_json = requests.post(url, headers=headers, data=data)

    #api = orcid.PublicAPI(client_id, client_secret, sandbox=True)
    #response = api.get_token_from_authorization_code(code, "localhost:5000")

    print(output_json)
    '''
    inputstr = 'client_id=' + client_id + '&client_secret=' + client_secret + '&grant_type=authorization_code&code=' + code
    output = subprocess.check_output(['curl', '-i', '-L', '-H', 'Accept: application/json', '--data', inputstr,  'https://sandbox.orcid.org/oauth/token'],universal_newlines=True)
    
    ind = output.index('{')
    output = output[ind:]
    output_json = json.loads(output)   
    session['orcid']= output_json['orcid']
    print(session['orcid'])
    return redirect(stage)
@app.route('/logout')
def logout():
    del session['orcid']
    return redirect(request.referrer)

@app.route('/auth')
def auth():
    return redirect("https://sandbox.orcid.org/oauth/authorize?client_id=APP-J5XDZ0YEXPLVSRMZ&response_type=code&scope=/authenticate&redirect_uri=https://p1of926o5h.execute-api.us-west-1.amazonaws.com/dev/login")

@app.route('/add-relationship', methods=["GET","POST"])
def add_relationship():
    g = GraphDB()
    topics = g.get_topics()

    status= "none"
    f=None

    if request.method == "POST":
        f = request.form
        print(request.form)
        status = "failure"
        #do checks and determite if submission is valid
        if validate_form(f):
            status = "success"
            APP = {
                    'topic': f['Topic'],
                    'name': f['Application_Name'],
                    'site': f['site'],
                    'screenshot': 'Testing 123.png',
                    'publication': f['Publication_Link'],
                    'description': 'example description 123'
            }
            DATASET = {'title': f['Dataset_Name'], 'doi': f['DOI']}

            #print(APP)
            #print(DATASET)
            #post data to DB
            g.add_app(APP)
            g.add_dataset(DATASET)
            g.add_relationship(f['Application_Name'],f['DOI'])
            
            #iterate through dataset list
            i = 0
            '''
            for key, value in f.items():
                if i >5:
                    DATASET = {'title': f[key], 'doi': f[key]}
                    g.add_dataset(DATASET)
                    g.add_relationship(f['Application_Name'],f[key])
                    
                    print(i, " : ", key, value)
                i+=1
            '''

        '''
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
        '''

    orcid = False
    if 'orcid' in session:
        orcid = True

    return render_template('add-relationship.html', stage=stage, status=status, form=f, topics=topics, orcid=orcid)

def validate_form(f):
    if f['Topic']=='Choose..':
        return False
    for item in f.values():
        if len(item)==0:
            return False
    if 'orcid' in session and session['orcid'] in trusted:
        return True
    return False

@app.route('/delete_dataset_relation/<app_name>/<doi>')
def delete_dataset_relation(app_name, doi):
    if 'orcid' in session and session['orcid'] in trusted:
        g = GraphDB() 
        #delete relationship function 
        g.delete_relationship(app_name, doi)
    return redirect(request.referrer)

if __name__ == '__main__':
    app.run(debug=True)

