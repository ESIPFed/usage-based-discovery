from util.graph_db import GraphDB
from util.s3_functions import s3Functions
from flask import Flask, url_for, render_template, request, session, redirect
from flask_fontawesome import FontAwesome
import requests
import json
import urllib
from util.autofill import autofill
from util.env_loader import load_env

from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.traversal import T

import os
import subprocess

app = Flask(__name__)
fa = FontAwesome(app)

app.secret_key = os.urandom(32)
#load_env()
stage = os.environ.get('STAGE')
client_secret = os.environ.get('CLIENT_SECRET')
client_id = os.environ.get('CLIENT_ID')
s3_bucket = os.environ.get('S3_BUCKET')

'''
# app layout
APP = {
    'topic': 'Test',
    'name': 'test_name',
    'site': 'https://example.com',
    'screenshot': 'Testing 123.jpg',
    'publication': 'None',
    'description': 'example description 123'
}

# session layout
Session = {
    'orcid': (String)'9999-9999-9999-9999' (property will not exist if not logged in)
    'role': (String)'supervisor','general' (property will not exist if not logged in)
    'changes': (List)Changes_made, a stack of changes make by a user (like a history) to be used to undo changes 
}

'''
# Initial screen
@app.route('/')
def home():
    g = GraphDB()
    print(g.get_topics())
    topic_list = sorted(g.get_topics())
    # attatch presigned url to each topic to get a topic icon to display
    s3 = s3Functions()
    screenshot_list = []
    for topic in topic_list:
        screenshot_list.append(s3.create_presigned_url(s3_bucket, 'topic/'+topic+'.jpg'))
    topics_screenshot_zip = zip(topic_list, screenshot_list)
    # in_session determines if the user is logged in, and if so they get their own privileges
    in_session = 'orcid' in session
    return render_template('init.html', stage=stage, topics_screenshot_zip=topics_screenshot_zip, in_session=in_session)

# Topic attribution
@app.route('/topic-attribution')
def topic_attribution():
    return render_template('topic-attribution.html', stage=stage)

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
    # encode all apps, and doi's, original app name and doi is in a seperate variable 
    app = urllib.parse.unquote(urllib.parse.unquote(app))    
    g = GraphDB()
    topics = sorted(g.get_topics())
    # query only for application relating to specified topic
    relapps = g.mapify(g.get_apps_by_topic(topic))
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
        appsel = g.mapify(g.get_app(app))
        appsel[0]['encoded_name'] = urllib.parse.quote(urllib.parse.quote(appsel[0]['name'], safe=''), safe='')
        filename = appsel[0]['screenshot']
        # query for all datasets relating to specified application
        datasets = g.get_datasets_by_app(app)
    s3 = s3Functions()
    filename = topic+'.png' if filename == 'NA' else filename
    screenshot = s3.create_presigned_url(s3_bucket, filename)
    
    in_session = 'orcid' in session
    trusted_user = 'role' in session and session['role']=='supervisor' 
    
    for d in datasets:
        print("dataset Path:       ", d)
        d[2]['encoded_doi']=urllib.parse.quote(urllib.parse.quote(d[2]['doi'][0], safe=''), safe='') #safe ='' is there to translate '/' to '%2f' because we don't want / in our urls

    undo = None
    if 'changes' in session and len(session['changes'])>0:
        undo = json.dumps(session['changes'][-1]['type'])
    return render_template('index.html', stage=stage, topic=topic, \
        topics=topics, apps=relapps, app=appsel, datasets=datasets, screenshot=screenshot, \
        in_session=in_session, trusted_user=trusted_user, undo=undo)

@app.route('/login')
def login():
    '''
    we get a code from the url that orcid has redirected us back to our site with. 
    that code can be used to access the users orcid data, mainly name and orc-id.
    we do a curl in a subprocess call with the code, to ask orcid for the users orcid data
    we get back the users orcid id, we check if the users orc-id is in our private s3-buckets orcid.json file and assign a role, and orc-id to that session
    '''
    code = request.args.get('code')
    inputstr = 'client_id=' + client_id + '&client_secret=' + client_secret + '&grant_type=authorization_code&code=' + code 
    output = subprocess.check_output(['curl', '-i', '-L', '-H', 'Accept: application/json', '--data', inputstr,  'https://orcid.org/oauth/token'],universal_newlines=True)
    
    ind = output.index('{')
    output = output[ind:]
    output_json = json.loads(output)
    
    s3 = s3Functions()
    data = s3.get_file(s3_bucket, 'orcid.json')
    data = json.loads(data)
    if output_json['orcid'] in data['supervisor']:
        session['role'] = 'supervisor'
    else:
        session['role'] = 'general'
    session['orcid']= output_json['orcid']
    return redirect(stage)

@app.route('/logout')
def logout():
    del session['orcid']
    del session['role']
    return redirect(request.referrer)

@app.route('/auth')
def auth():
    '''
    send the user to orcid with our app's client_id
    after the user logs in, they will be redirected to the '/login' route with code
    '''
    redirect_uri = request.url_root + "/login"
    return redirect("https://orcid.org/oauth/authorize?client_id=" + client_id + "&response_type=code&scope=/authenticate&redirect_uri=" + redirect_uri)

@app.route('/add-relationship', methods=["GET","POST"])
def add_relationship():
    '''
    only allowing people logged in to be able to add-relationships
    for it to be posted to the database they must also be trusted users
    
    This is a very complex seeming route, so let me break it down. 
    This route is called in 3 scenarios:
    1. When you want to add a application and the datasets that belong with it
    2. When you want to edit an existing application
    3. when you call autofill from the form, it will also use this route to know what to do with the autofilled components
   
    Both edit application and autofill use the post request method to this route to post the data into the form
    
    '''
    if 'orcid' not in session:
        redirect_uri = request.url_root + "/login"
        return redirect("https://orcid.org/oauth/authorize?client_id=" + client_id + "&response_type=code&scope=/authenticate&redirect_uri=" + redirect_uri)
    orcid = 'orcid' in session
    role = session['role'] 

    g = GraphDB()
    topics = g.get_topics()
    status= "none"
    f=None

    if request.method == "POST":
        #since request.form is an immutable obj, we would like to copy it to something mutable
        f={}
        for key, value in request.form.items():
            print(key,value)
            f[key] = value
        f['Topic[]'] = request.form.getlist('Topic[]') # used to get the multiple values of 'Topic[]'
        print(f)
        status = "failure"

        #we use try block because autofill errors out when the url is not found
        try:
            #check if the form is submitted with the autofill tag
            if 'autofill' in f and f['autofill']=='true':
                status= ""
                fill = autofill(f['site'])
                datasets_obj = fill['datasets']
                #if description/App name is not filled in then autofill them
                if f['description'] == '':
                    f['description'] = fill['description']
                if f['Application_Name'] == '':
                    f['Application_Name'] = fill['name']
                if len(f['Topic[]'])==0:
                    f['Topic[]'] = [fill['topic'] if fill['topic']!='Miscellaneous' else '']
                for index, item in enumerate(datasets_obj):
                    title = item[0]
                    doi = item[1]
                    f["Dataset_Name_"+ str(index+10)]=title
                    f["DOI_" + str(index+10)]= doi
                return render_template('add-relationship.html', stage=stage, status=status, form=f, topics=topics, role=role)
        except:
            status = "invalid URL"
            return render_template('add-relationship.html', stage=stage, status=status, form=f, topics=topics, orcid=orcid, role=role)

        #Filling in the form when users try to edit an app
        if 'type' in f and f['type'] == 'edit_application':
            status = "edit_application"
            datasets_obj = g.get_datasets_by_app(f['name'])
            app = g.mapify(g.get_app(f['name']))[0]
            print("got app:    ", app)
            f['Application_Name'] = f['name']
            f['description'] = app['description']
            f['Topic[]'] = g.get_app_topics(f['name'])
            f['site'] = app['site']
            f['Publication_Link'] = app['publication']
            #iterating through datasets so they also show up in form
            for index, item in enumerate(datasets_obj):
                title = item[2]['title'][0]
                doi = item[2]['doi'][0]
                f['Dataset_Name_'+str(index+10)] = title
                f['DOI_'+str(index+10)] = doi
            return render_template('add-relationship.html', stage=stage, status=status, form=f, topics=topics, orcid=orcid, role=role)

        #check if submission is valid, if valid then we upload the content
        if validate_form(f):
            f['screenshot'] = 'NA'
            
            # get previous app information if there was one, ( 'prev_app_name will be a property of the form when you edit an application) 
            if 'prev_app_name' in f:
                #store screenshot info before app deletion
                temp_app = g.mapify(g.get_app(f['prev_app_name']))
                f['screenshot'] = temp_app[0]['screenshot']

            APP = {
                    'topic': f['Topic[]'],
                    'name': f['Application_Name'],
                    'site': f['site'],
                    'screenshot': f['screenshot'],
                    'publication': f['Publication_Link'],
                    'description': f['description'] 
            }
            #logic to add topics that are custom if authorized
            if session['role'] == 'supervisor':
                for topic in APP['topic']:
                    g.add_topic(topic)
            g.update_app(f['prev_app_name'],APP) if 'prev_app_name' in f else g.add_app(APP)
            #iterate through the forms dataset list
            list_of_datasets = []
            list_of_DOIs = []
            for key,value in f.items(): 
                #added datasets all have the last character as a digit
                if key[-1].isdigit():
                    if key[:4] =="Data":
                        list_of_datasets.append(value)
                    if key[:4] =="DOI_":
                        list_of_DOIs.append(value)
            # upload lists of datasets/dois to db
            for Dataset_name, DOI in zip(list_of_datasets, list_of_DOIs):
                DATASET = {'title': Dataset_name, 'doi': DOI}
                if g.has_dataset(DOI):
                    g.update_dataset(DOI, DATASET)
                else:
                    g.add_dataset(DATASET)
                g.add_relationship(f['Application_Name'],DOI)
            #if the DB has a DOI that the form doesn't then remove that relationship
            datasets = g.get_datasets_by_app(f['Application_Name'])
            temp_app = g.mapify(g.get_app(f['Application_Name']))
            for dataset in datasets:
                if dataset[2]['doi'][0] not in list_of_DOIs:
                    g.delete_relationship(temp_app[0]['name'], dataset[2]['doi'][0])
            g.delete_orphan_datasets()
            status = "success"
    return render_template('add-relationship.html', stage=stage, status=status, form=f, topics=topics, orcid=orcid, role=role)

def validate_form(f):
    #potentially do some checks here before submission into the db
    if 'role' in session and session['role']=='supervisor':
        return True
    return False

@app.route('/delete_dataset_relation/<encoded_app_name>/<encoded_doi>')
def delete_dataset_relation(encoded_app_name, encoded_doi):
    # double decode to avoid apache %2F translation, so %252F goes to %2F which goes to /
    doi = urllib.parse.unquote(urllib.parse.unquote(encoded_doi)) 
    app_name = urllib.parse.unquote(urllib.parse.unquote(encoded_app_name))
    if 'role' in session and session['role']=='supervisor':
        g = GraphDB() 
        #log this change in session to be able to undo later
        #dataset = g.mapify(g.get_dataset(doi))[0]
        dataset_path = g.get_dataset_by_app(app_name,doi)[0]
        change = {
                    'type': 'delete_dataset_relation',
                    'dataset_and_edge': [g.mapify([dataset_path[2]])[0], dataset_path[1]],
                    'app_name': app_name,
                }
        if 'changes' in session:
            temp_changes = session['changes']
            temp_changes.append(change)
            session['changes'] = temp_changes
        else:
            session['changes'] = [change]
        print("this is dataset change" , session['changes'])
        # after logging, delete the relationship 
        g.delete_relationship(app_name, doi)
        g.delete_orphan_datasets()
    return redirect(request.referrer)

@app.route('/delete_application/<encoded_app_name>')
def delete_application(encoded_app_name):
    # double decode to avoid apache %2F translation, so %252F goes to %2F which goes to /
    app_name = urllib.parse.unquote(urllib.parse.unquote(encoded_app_name))
    if 'role' in session and session['role']=='supervisor':
        g = GraphDB() 
        #session 'changes' keeps a history of all changes made by that user
        #before we delete application we need to store all the info so we can undo
        app = g.mapify(g.get_app(app_name))
        app[0]['topic'] = g.get_app_topics(app_name)
        dataset_paths = g.get_datasets_by_app(app_name)
        datasets_and_edges = []
        for path in dataset_paths:
            edge = path[1]
            path = g.mapify([path[2]])
            datasets_and_edges.append([path[0],edge])
        change = {
            'type': 'delete_application',
            'app': app[0],
            'datasets_and_edges': datasets_and_edges,
        }
        if 'changes' in session:
            temp_changes= session['changes']
            temp_changes.append(change)
            session['changes'] = temp_changes
        else:
            session['changes'] = [change]
        print("this is application change", session['changes'])
        #delete application
        g.delete_app(app_name)
        g.delete_orphan_datasets()
    redirect_path = request.referrer.rsplit('/',1)[0] + '/all' # this is so we direct to /topic/all instead of topic/app (topic/app doesn't exit after it gets deleted)
    return redirect(redirect_path)

@app.route('/undo')
def undo():
    change = None
    #create stack implementation to make undo's 
    if 'changes' in session and len(session['changes'])>0:
        g = GraphDB()
        temp = session['changes']
        change = temp.pop()
        print("change to undo:   ", change)
        session['changes'] = temp
        if change['type'] =="delete_dataset_relation":
            dataset = change['dataset_and_edge'][0]
            edge = change['dataset_and_edge'][1]
            g.add_dataset(dataset)
            g.add_relationship(change['app_name'], dataset['doi'], edge['discoverer'], edge['verified'], edge['verifier'])
        elif change['type'] == "delete_application":
            #adding the deleted app back
            g.add_app(change['app'])
            for dataset, edge in change['datasets_and_edges']:
                #adding each dataset back and linking it to the app
                g.add_dataset(dataset)
                g.add_relationship(change['app']['name'], dataset['doi'], edge['discoverer'], edge['verified'], edge['verifier'])
        else:
            print("type not found")
        return redirect(request.referrer)
    return redirect(request.referrer)

@app.route('/verify/<encoded_app_name>/<encoded_doi>')
def verify(encoded_app_name, encoded_doi):
    doi = urllib.parse.unquote(urllib.parse.unquote(encoded_doi)) 
    app_name = urllib.parse.unquote(urllib.parse.unquote(encoded_app_name))
    g = GraphDB()
    if 'role' in session and session['role'] == 'supervisor':
        g.verify_relationship(app_name, doi, session['orcid'])
    return redirect(request.referrer)

def unhandled_exceptions(e, event, context):
    send_to_raygun(e, event)  # gather data you need and send
    return True # Prevent invocation retry

if __name__ == '__main__':
    app.run(debug=True)
