from dotenv import load_dotenv
load_dotenv()

from util.graph_db import GraphDB
from util.s3_functions import s3Functions
from flask import Flask, url_for, render_template, request, session, redirect
from flask_fontawesome import FontAwesome
import json
from util.autofill import autofill

from util.add_csv import db_input_csv
import os
import subprocess
from util import secrets_manager

from PIL import Image
import io

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
fa = FontAwesome(app)

if os.environ.get('ENV') == 'local-app':
    app.secret_key = os.environ.get('APP_SECRET_KEY')
else:
    app.secret_key = secrets_manager.get_secret('APP_SECRET_KEY')
client_secret = os.environ.get('CLIENT_SECRET')
client_id = os.environ.get('CLIENT_ID')
s3_bucket = os.environ.get('S3_BUCKET')


types = [
            'unclassified',
            'Software',
            'Research'
        ]
'''
# app layout
APP = {
    'name': 'test_name',
    'site': 'https://example.com',
    'type': [<type_1>, <type_2>] #multi-property so it returns as a list in value_map graph function
    'screenshot': 'Testing-123.png',
    'publication': 'None' or '<url>',
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
def topics():
    string_type = request.args.get('string_type') or 'all'
    # string_type is in this format: "<type>,<type2>,<type3>"
    Type = string_type.split(',')
    g = GraphDB()
    if string_type == 'all':
        Type = types
        string_type= 'all'
    topic_list = sorted(g.get_topics_by_types(Type))
    # attatch presigned url to each topic to get a topic icon to display
    s3 = s3Functions()
    screenshot_list = []
    for topic in topic_list:
        screenshot_list.append(s3.create_presigned_url(s3_bucket, 'topic/'+topic+'.jpg'))
    topics_screenshot_zip = zip(topic_list, screenshot_list)
    # in_session determines if the user is logged in, and if so they get their own privileges
    in_session = 'orcid' in session
    return render_template('topics.html', topics_screenshot_zip=topics_screenshot_zip, in_session=in_session, Type=Type, string_type=string_type)

# Topic attribution
@app.route('/topic-attribution')
def topic_attribution():
    in_session = 'orcid' in session
    return render_template('topic-attribution.html', in_session=in_session)

# About page
@app.route('/about')
def about():
    in_session = 'orcid' in session
    return render_template('about.html', in_session=in_session)

@app.route('/explore')
def explore():
    in_session = 'orcid' in session
    g = GraphDB()
    data = g.get_data()
    return render_template('graph.html', data=data, in_session=in_session)

"""
To-Do: only refresh the app/datasets when you select another type/topic
"""

# Main screen
@app.route('/apps')
def apps():
    app_site = request.args.get('app_site')
    string_type = request.args.get('string_type')
    string_topic = request.args.get('string_topic')

    in_session = 'orcid' in session
    trusted_user = 'role' in session and session['role']=='supervisor' 

    g = GraphDB()
    
    Type = string_type.split(',')
    topic = string_topic.split(',')
    
    if 'all' in Type:
        Type = types

    topics = sorted(g.get_topics_by_types(Type))
    Types = sorted(g.get_types_by_topics(topic))
    
    topic = topic[0] # take this out later once multi select is in
    
    # query only for application relating to specified topic and type
    topic_apps = g.mapify(g.api( [topic] , Type))
    # filter apps and datasets based on if they are trusted
    if not trusted_user:
        topic_apps = list(filter(lambda relapp: relapp['verified']==True, topic_apps))
    topic_apps.sort(key=lambda x: x['name'], reverse=False)

    selected_app = None
    if(app_site != 'all'):
        selected_app = g.mapify(g.get_app(app_site))[0]
    elif(len(topic_apps) != 0):
        selected_app=topic_apps[0]
    
    # query for all datasets relating to specified application
    datasets = g.get_datasets_by_app(selected_app['site'])
    datasets.sort(key=lambda d: d[2]['title'][0], reverse=False)

    #getting temporary images for apps who don't have images
    s3 = s3Functions()
    filename = 'topic/'+topic+'.jpg' 
    if selected_app is not None and selected_app['screenshot'] != 'NA':
        filename = selected_app['screenshot']
    screenshot = s3.create_presigned_url(s3_bucket, filename)
    
    undo = None
    if 'changes' in session and len(session['changes'])>0:
        undo = json.dumps(session['changes'][-1]['type'])

    return render_template('apps.html',\
        topic=topic, Type=Type, topics=topics, Types=Types, all_types=types,\
        string_topic=string_topic, string_type=string_type, apps=topic_apps,\
        app=selected_app, datasets=datasets, screenshot=screenshot, \
        in_session=in_session, trusted_user=trusted_user, undo=undo)

@app.route('/login')
def login():
    '''
    we get a code from the url that orcid has redirected us back to our site with. 
    that code can be used to access the users orcid data, mainly name and orc-id.
    we do a curl in a subprocess call with the code, to ask orcid for the users orcid data
    we get back the users orcid id, we check if the users orc-id is in our private s3-buckets orcid.json file and assign a role, and orc-id to that session
    '''
    orcid = None
    if os.environ.get('ENV') == 'local-app': #bypass oauth call
        orcid = os.environ.get('ORCID')
    else:
        code = request.args.get('code')
        inputstr = 'client_id=' + client_id + '&client_secret=' + client_secret + '&grant_type=authorization_code&code=' + code 
        output = subprocess.check_output(['curl', '-i', '-L', '-H', 'Accept: application/json', '--data', inputstr,  'https://orcid.org/oauth/token'],universal_newlines=True)
        
        ind = output.index('{')
        output = output[ind:]
        output_json = json.loads(output)
        orcid = output_json['orcid']
    
    s3 = s3Functions()
    data = s3.get_file(s3_bucket, 'orcid.json')
    data = json.loads(data)
    if orcid in data['supervisor']:
        session['role'] = 'supervisor'
    else:
        session['role'] = 'general'
    session['orcid']= orcid
    return redirect(url_for('topics'))

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
    if os.environ.get('ENV') == 'local-app':
        # bypass the orcid api
        return redirect(url_for('login'))

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
        if os.environ.get('ENV') == 'local-app':
            # bypass the orcid api
            return redirect(url_for('login'))
        else:
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
        # Getting multiple values of 'Topic[]', 'Type[]'; empty if non-existant
        f['Topic[]'] = request.form.getlist('Topic[]')
        f['Type[]'] = request.form.getlist('Type[]')
        print(f)
        status = "failure" # preset 

        #we use try block because autofill errors out when the url is not found
        try:
            #check if the form is submitted with the autofill tag
            if 'autofill' in f and f['autofill']=='true':
                auto_fill(f)
                status= ""
                return render_template('add-relationship.html', status=status, form=f, topics=topics,types=types, role=role, in_session=orcid)
        except:
            status = "invalid URL"
            return render_template('add-relationship.html', status=status, form=f, topics=topics, types=types, orcid=orcid, role=role, in_session=orcid)

        # Filling in the form when users try to edit an app
        if 'type' in f and f['type'] == 'edit_application':
            status = "edit_application"
            edit_application(f, g)
            return render_template('add-relationship.html', status=status, form=f, topics=topics, types=types, orcid=orcid, role=role, in_session=orcid)

        # Check if submission is valid, if valid then we upload the content
        if validate_form(f):
            f['screenshot'] = 'NA'
            APP = formatted_APP_from_form(f, g)
            if os.environ.get('ENV') != 'local-app':
                upload_screenshot(APP, request)
            else:
                print('Bypassing screenshot upload')
            print(f"App screenshot was set to {APP['screenshot']}")

            # Logic to add topics that are custom if authorized
            if session['role'] == 'supervisor':
                for topic in APP['topic']:
                    g.add_topic(topic)
                if 'prev_app_site' in f:
                    print("this is previous app:\n", g.get_app(f['prev_app_site']))
                g.update_app(f['prev_app_site'], APP) if 'prev_app_site' in f else g.add_app(APP, discoverer=session['orcid'], verified=True, verifier=session['orcid']) 
                print("this is NEW app:\n", g.get_app(APP['site']))
            elif 'prev_app_site' not in f:
                g.add_app(APP, discoverer=session['orcid']) # submitted as unverified (general user submitted)
            else: 
                return render_template('add-relationship.html', status=status, form=f, topics=topics, types=types, orcid=orcid, role=role, in_session=orcid)

            #iterate through the forms dataset list
            upload_datasets_from_form(f, g, APP, session)
            status = "success"

    return render_template('add-relationship.html', status=status, form=f, topics=topics, types=types, orcid=orcid, role=role, in_session=orcid)

def auto_fill(f):
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
        #adding 10 to the dataset/doi form property since there might be previous ds/doi in the earlier numbers
        f["Dataset_Name_"+ str(index+10)]=title
        f["DOI_" + str(index+10)]= doi

# Modifying the the form so it is filled with the App's info 
def edit_application(f, g):
    datasets_obj = g.get_datasets_by_app(f['app_site'])
    app = g.mapify(g.get_app(f['app_site']))[0]
    print("got app:    ", app)
    f['type[]'] = app['type']
    f['Application_Name'] = app['name']
    f['description'] = app['description']
    f['Topic[]'] = g.get_app_topics(app['site'])
    f['site'] = app['site']
    f['Publication_Link'] = app['publication']
    # Iterating through datasets so they also show up in form
    for index, item in enumerate(datasets_obj):
        title = item[2]['title'][0]
        doi = item[2]['doi'][0]
        f['Dataset_Name_'+str(index+10)] = title
        f['DOI_'+str(index+10)] = doi

def validate_form(f):
    #potentially do some checks here before submission into the db
    if 'role' in session:
        return True
    return False

def formatted_APP_from_form(f, g):
    # Get previous app information if there was one(mainly for the screenshot info), ( 'prev_app_name' will be a property of the form when you edit an application) 
    if 'prev_app_site' in f:
        # Store screenshot info before app deletion
        temp_app = g.mapify(g.get_app(f['prev_app_site']))
        f['screenshot'] = temp_app[0]['screenshot']
    # There are alot of things in f (submitted form) that we don't want when adding just an app(like datasets), so we filter the data into APP
    APP = {
            'type': f['Type[]'],
            'topic': f['Topic[]'],
            'name': f['Application_Name'],
            'site': f['site'],
            'screenshot': f['screenshot'],
            'publication': f['Publication_Link'],
            'description': f['description'] 
    }
    return APP

def resize_image_file(image_file):
    pil_image = Image.open(image_file)
    pil_image.thumbnail((400, 400))
    new_file = io.BytesIO()
    pil_image.save(new_file, format=pil_image.format, optimize=True)
    new_file.seek(0)

    return new_file

def upload_screenshot(APP, request):
    if 'image_file' in request.files.keys() and request.files['image_file'].filename != '':
        print(f"Request contains image screenshot { request.files['image_file'] }")
        file_name = request.files['image_file'].filename
        resized_image = resize_image_file(request.files['image_file'])
        s3 = s3Functions()
        s3.upload_image_obj(s3_bucket, file_name, resized_image)
        APP['screenshot'] = file_name
    else:
        print('Request is missing screenshot')

def upload_datasets_from_form(f, g, APP, session):
    discoverer = session['orcid'] if 'orcid' in session else ''
    list_of_datasets = []
    list_of_DOIs = []
    for key,value in f.items(): 
        #added datasets all have the last character as a digit
        if key[-1].isdigit():
            # adding all the dataset and doi's of the form to two lists to be added in pairs
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
        g.add_relationship(f['site'],DOI, discoverer=discoverer)
    #if the DB has a DOI that the form doesn't then remove that relationship
    datasets = g.get_datasets_by_app(APP['site'])
    for dataset in datasets:
        if dataset[2]['doi'][0] not in list_of_DOIs:
            print('Dataset DOI:\n\n', dataset[2]['doi'][0], 'site:\n', APP['site'])
            g.delete_relationship(APP['site'], dataset[2]['doi'][0])
    g.delete_orphan_datasets()

@app.route('/delete_dataset_relation')
def delete_dataset_relation():
    app_site = request.args.get('app_site')
    doi = request.args.get('doi')
    if 'role' in session and session['role']=='supervisor':
        g = GraphDB() 
        #log this change in session to be able to undo later
        #dataset = g.mapify(g.get_dataset(doi))[0]

        print('app_site:\n\n\n', app_site, 'doi:\n\n\n', doi)

        dataset_path = g.get_dataset_by_app(app_site, doi)[0]
        change = {
                    'type': 'delete_dataset_relation',
                    'dataset_and_edge': [g.mapify([dataset_path[2]])[0], dataset_path[1]],
                    'app_site': app_site,
                }
        if 'changes' in session:
            temp_changes = session['changes']
            temp_changes.append(change)
            session['changes'] = temp_changes
        else:
            session['changes'] = [change]
        print("this is dataset change" , session['changes'])
        # after logging, delete the relationship 
        g.delete_relationship(app_site, doi)
        g.delete_orphan_datasets()
    return redirect(request.referrer)

@app.route('/delete_application')
def delete_application():
    app_site = request.args.get('app_site')
    if 'role' in session and session['role']=='supervisor':
        g = GraphDB() 
        #session 'changes' keeps a history of all changes made by that user
        #before we delete application we need to store all the info so we can undo
        app = g.mapify(g.get_app(app_site))
        app[0]['topic'] = g.get_app_topics(app_site)
        dataset_paths = g.get_datasets_by_app(app_site)
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
        g.delete_app(app_site)
        g.delete_orphan_datasets()
    redirect_path = request.referrer.rsplit('/',1)[0] + '/all' # this is so we direct to .../topic/all instead of .../topic/app (topic/app doesn't exit after it gets deleted)
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
            g.add_relationship(change['app_site'], dataset['doi'], edge['discoverer'], edge['verified'], edge['verifier'], edge['annotation'])
        elif change['type'] == "delete_application":
            #adding the deleted app back
            g.add_app(change['app'], change['app']['discoverer'], change['app']['verified'], change['app']['verifier'])
            for dataset, edge in change['datasets_and_edges']:
                #adding each dataset back and linking it to the app
                g.add_dataset(dataset)
                g.add_relationship(change['app']['site'], dataset['doi'], edge['discoverer'], edge['verified'], edge['verifier'], edge['annotation'])
        else:
            print("type not found")
        return redirect(request.referrer)
    return redirect(request.referrer)

@app.route('/verify-application')
def verify_application():
    app_site = request.args.get('app_site')
    g = GraphDB()
    if 'role' in session and session['role'] == 'supervisor':
        g.verify_app(app_site, session['orcid'])
    return redirect(request.referrer)

@app.route('/verify-dataset')
def verify_dataset():
    app_name = request.args.get('app_name')
    doi = request.args.get('doi')
    g = GraphDB()
    if 'role' in session and session['role'] == 'supervisor':
        g.verify_relationship(app_name, doi, session['orcid'])
    return redirect(request.referrer)

@app.route('/add_annotation', methods=["GET", "POST"])
def add_annotation():
    app_site = request.args.get('app_site')
    doi = request.args.get('doi')
    if request.method == 'POST':
        f = request.form
        g = GraphDB()
        g.add_annotation(app_site, doi, f['annotation'])
    return redirect(request.referrer)

@app.route('/resolve_annotation')
def resolve_annotation():
    app_site = request.args.get('app_site')
    doi = request.args.get('doi')
    g = GraphDB()
    g.add_annotation(app_site, doi, '')
    return redirect(request.referrer)


@app.route('/add-csv', methods=["GET", "POST"])
def add_csv():
    print(request.files)
    if request.method=="POST" and session['role']=='supervisor':
        uploaded_file = request.files['csv_file']
        if uploaded_file.filename != '':
            fstring = uploaded_file.read()
            fstring = fstring.decode("utf-8")
            did_it_work = db_input_csv(fstring, session['orcid'])
            print(did_it_work)
            return "CSV values successfully added"
    return "Please check data headers and try again"

def parse_stats(app_stat_keys, app_list):
    app_stats = {}
    for app_stat_key in app_stat_keys:
        key_stats = {}
        for app in app_list:
            if app_stat_key in app:
                stat_value = None
                if isinstance(app[app_stat_key], list):
                    stat_value = app[app_stat_key][0]
                else:
                    stat_value = app[app_stat_key]
                if stat_value in key_stats:
                    key_stats[stat_value] +=1
                else:
                    key_stats[stat_value] = 1
        key_stats = {k: v for k, v in sorted(key_stats.items(), key=lambda x: x[1], reverse=True)}
        app_stats[app_stat_key] = key_stats
    return app_stats

@app.route('/leader-board', methods=["GET"])
def leader_board():
    orcid = None
    in_session = 'orcid' in session
    if in_session:
        orcid = session['orcid']

    g = GraphDB()
    leader_board_data = g.get_leader_board()
    
    stat_keys = ['discoverer', 'verifier']

    app_list = leader_board_data['apps']
    app_stats = parse_stats(stat_keys, app_list)
    
    uses_list = leader_board_data['uses']
    uses_stats = parse_stats(stat_keys, uses_list)

    return render_template('leader-board.html', stats={'apps': app_stats, 'datasets': uses_stats}, in_session=in_session, orcid=orcid)


'''
Add this in when you create the 404,400,500.html. 

@app.errorhandler(404)
def not_found():
    """Page not found."""
    return make_response(
        render_template("404.html"),
        404
     )


@app.errorhandler(400)
def bad_request():
    """Bad request."""
    return make_response(
        render_template("400.html"),
        400
    )


@app.errorhandler(500)
def server_error():
    """Internal server error."""
    return make_response(
        render_template("500.html"),
        500
    )
'''
def unhandled_exceptions(e, event, context):
    send_to_raygun(e, event)  # gather data you need and send
    return True # Prevent invocation retry

if __name__ == '__main__':
    app.run(debug=True)
