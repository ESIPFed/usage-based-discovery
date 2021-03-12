from util.graph_db import GraphDB
from util.s3_functions import s3Functions
from flask import Flask, render_template, request, session, redirect
#from model import RegForm
import requests
import orcid
import json
import urllib

from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.traversal import T

import os
import subprocess

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY')
stage = os.environ.get('STAGE')
client_secret = os.environ.get('CLIENT_SECRET')
client_id = os.environ.get('CLIENT_ID')
trusted= {
            '0000-0002-3675-5603':'Parth Darji',
            '0000-0002-0868-7412':'Sophia Xia',
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
    # encode all apps, and doi's , keep the original app name and doi in a seperate variable or as property
    # we decode app in this route, and we decode the doi name in the delete ds route
    
    app = urllib.parse.unquote(urllib.parse.unquote(app))    
    g = GraphDB()
    topics = g.get_topics()
    # query only for application relating to specified topic
    relapps = g.get_apps_by_topic(topic)
    # double encoding relapps to avoid special characters issues
    for relapp in relapps:
        relapp['encoded_name'] = urllib.parse.quote(urllib.parse.quote(relapp['name'], safe=''), safe='') #safe ='' is there to translate '/' to '%2f' because we don't want / in our urls

    # query for the first application in relapps list
    if(app == 'all'):
        appsel = None
        # query for datasets related to the topic
        datasets = g.get_datasets_by_topic(topic)
        filename = relapps[0]['screenshot']
    # query for single application (vertex) with name specified by parameter
    else:
        appsel = g.get_app(app)
        appsel[0]['encoded_name'] = urllib.parse.quote(urllib.parse.quote(appsel[0]['name'], safe=''), safe='')
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

    for d in datasets:
        d['encoded_doi']=urllib.parse.quote(urllib.parse.quote(d['doi'], safe=''), safe='') #safe ='' is there to translate '/' to '%2f' because we don't want / in our urls
    
    undo = session['change'][-1]
    return render_template('index.html', stage=stage, topic=topic, \
        topics=topics, apps=relapps, app=appsel, datasets=datasets, screenshot=screenshot, \
        in_session=in_session, trusted_user=trusted_user, undo=undo)

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

            #post data to db
            g.add_app(APP)
            g.add_dataset(DATASET)
            g.add_relationship(f['Application_Name'],f['DOI'])
            
            #iterate through the forms dataset list
            
            list_of_datasets = []
            list_of_DOIs = []
            for key,value in f.items(): 
                if key[-1].isdigit():
                    if key[:4] =="Data":
                        list_of_datasets.append(value)
                    if key[:4] =="DOI_":
                        list_of_DOIs.append(value)
            print(list_of_datasets)
            print(list_of_DOIs)
           
            # upload lists of datasets/dois to db
            i = 0
            for Dataset_name, DOI in zip(list_of_datasets, list_of_DOIs):
                DATASET = {'title': Dataset_name, 'doi': DOI}
                g.add_dataset(DATASET)
                g.add_relationship(f['Application_Name'],DOI)
                print(i, " : ", Dataset_name, DOI)
                i+=1

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

@app.route('/delete_dataset_relation/<encoded_app_name>/<encoded_doi>')
def delete_dataset_relation(encoded_app_name, encoded_doi):
    # double decode to avoid apache %2F translation, so %252F goes to %2F which goes to /
    doi = urllib.parse.unquote(urllib.parse.unquote(encoded_doi)) 
    app_name = urllib.parse.unquote(urllib.parse.unquote(encoded_app_name))
    if 'orcid' in session and session['orcid'] in trusted:
        g = GraphDB() 
        #log this change in session to be able to undo later
        dataset = g.get_dataset(doi)
        change = {
                    'type': 'delete_dataset_relation',
                    'dataset': dataset,
                    'app_name': app_name,
                }
        if 'changes' in session:
            temp_changes = session['changes']
            temp_changes.append(change)
            session['changes'] = temp_changes
        else:
            session['changes'] = [change]
        print("this is dataset change" , session['changes'])
        #delete relationship function 
        g.delete_relationship(app_name, doi)
    return redirect(request.referrer)

@app.route('/delete_application/<encoded_app_name>')
def delete_application(encoded_app_name):
    # double decode to avoid apache %2F translation, so %252F goes to %2F which goes to /
    app_name = urllib.parse.unquote(urllib.parse.unquote(encoded_app_name))
    if 'orcid' in session and session['orcid'] in trusted:
        g = GraphDB() 
        #session 'changes' keeps a history of all changes made by that user
        #before we delete application we need to store all the info so we can undo
        app = g.get_app(app_name)
        datasets = g.get_datasets_by_app(app_name)
        change = {
            'type': 'delete_application',
            'app': app[0],
            'datasets': datasets,
        }
        print(change)
        if 'changes' in session:
            temp_changes= session['changes']
            temp_changes.append(change)
            session['changes'] = temp_changes
        else:
            session['changes'] = [change]
        print("this is application change", session['changes'])
        #delete application
        g.delete_app(app_name)
    redirect_path = request.referrer.rsplit('/',1)[0] + '/all' # this is so we direct to /topic/all instead of topic/app
    return redirect(redirect_path)

@app.route('/undo')
def undo():
    ############ maybe try session.modified=True ########
    change = None
    #create stack implementation to make undo's 
    if 'changes' in session and len(session['changes'])>0:
        g = GraphDB()
        print("entire session", session['changes'])
        temp = session['changes']
        change = temp.pop()
        session['changes'] = temp
        print("\n\nprinting Change\n\n", change)
        print("printing entire session again", session['changes'])
        if change['type'] =="delete_dataset_relation":
            g.add_dataset(change['dataset'])
            g.add_relationship(change['app_name'], change['dataset']['doi'])
        elif change['type'] == "delete_application":
            #adding the deleted app back
            g.add_app(change['app'])
            for d in change['datasets']:
                #adding each dataset back and linking it to the app
                g.add_dataset(d)
                g.add_relationship(change['app']['name'], d['doi'])
        else:
            print("type not found")
        return redirect(request.referrer)
    return redirect(request.referrer)# send a message "no more changes to undo"


if __name__ == '__main__':
    app.run(debug=True)

