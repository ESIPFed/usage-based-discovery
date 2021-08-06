from flask import request, session, redirect, render_template, url_for
from util import graph_db, essential_variables, usage_types
from util.autofill import AutoFill
from util.add_csv import db_input_csv
from routes.helper import thumbnail
import os

def auto_fill(f):
    fill = AutoFill.autofill(f['site'])
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
    if 'essential_variable' in app:
        f['essential_variable'] = app['essential_variable']
    f['Topic[]'] = g.get_app_topics(app['site'])
    f['site'] = app['site']
    f['Publication_Link'] = app['publication']
    # Iterating through datasets so they also show up in form
    for index, item in enumerate(datasets_obj):
        title = item[2]['title'][0]
        doi = item[2]['doi'][0]
        f['Dataset_Name_'+str(index+10)] = title
        f['DOI_'+str(index+10)] = doi

def sanitize_app(APP):
    if 'Research' in APP['type']:
        del APP['screenshot']
        del APP['publication']
    return APP

def validate_form(f):
    #potentially do some checks here before submission into the db
    if 'role' in session:
        return True
    return False

def formatted_APP_from_form(f, g):
    # Get previous app information if there was one(mainly for the screenshot info), ( 'prev_app_name' will be a property of the form when you edit an application) 
    if 'prev_app_site' in f and f['prev_app_site']:
        temp_app = g.mapify(g.get_app(f['prev_app_site']))
        f['screenshot'] = temp_app[0].get('screenshot')
    # There are alot of things in f (submitted form) that we don't want when adding just an app(like datasets), so we filter the data into APP
    APP = {
        'type': f['Type[]'],
        'topic': f['Topic[]'],
        'name': f['Application_Name'],
        'site': f['site'],
        'screenshot': f['screenshot'],
        'publication': f['Publication_Link'],
        'description': f['description'],
        'essential_variable': f['essential_variable']  
    }
    return APP

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
    print(request.form)
    if 'orcid' not in session:
        if os.environ.get('FLASK_ENV') == 'development':
            # bypass the orcid api
            return redirect(url_for('login'))
        else:
            redirect_uri = request.url_root + "/login"
            return redirect("https://orcid.org/oauth/authorize?client_id=" + os.environ.get('CLIENT_ID') \
                + "&response_type=code&scope=/authenticate&redirect_uri=" + redirect_uri)
    orcid = 'orcid' in session
    role = session['role'] 

    g = graph_db.GraphDB()
    topics = sorted(g.get_topics())
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
        f['essential_variable'] = request.form.getlist('essential_variable')
        print(f)
        status = "failure" # preset 

        #we use try block because autofill errors out when the url is not found
        try:
            #check if the form is submitted with the autofill tag
            if 'autofill' in f and f['autofill']=='true':
                auto_fill(f)
                status= ""
                return render_template('add-relationship.html', status=status, form=f, topics=topics,types=usage_types.values, 
                    role=role, in_session=orcid, essential_variables=essential_variables.values)
        except:
            status = "invalid URL"
            return render_template('add-relationship.html', status=status, form=f, topics=topics, types=usage_types.values, 
                orcid=orcid, role=role, in_session=orcid, essential_variables=essential_variables.values)

        # Filling in the form when users try to edit an app
        if 'type' in f and f['type'] == 'edit_application':
            status = "edit_application"
            edit_application(f, g)
            return render_template('add-relationship.html', status=status, form=f, topics=topics, types=usage_types.values, 
                orcid=orcid, role=role, in_session=orcid, essential_variables=essential_variables.values)

        # Check if submission is valid, if valid then we upload the content
        if validate_form(f):
            f['screenshot'] = 'NA'
            APP = formatted_APP_from_form(f, g)
            file_name = thumbnail.upload_thumbnail(request, (400, 400))
            if file_name:
                APP['screenshot'] = file_name
            else:
                print('Bypassing screenshot upload')
            print(f"App screenshot was set to {APP['screenshot']}")

            APP = sanitize_app(APP)

            # Logic to add topics that are custom if authorized
            if session['role'] == 'supervisor':
                for topic in APP['topic']:
                    g.add_topic(topic)
                if 'prev_app_site' in f:
                    print("this is previous app:\n", g.get_app(f['prev_app_site']))
                if 'prev_app_site' in f:
                        g.update_app(f['prev_app_site'], APP)
                else:
                    g.add_app(APP, discoverer=session['orcid'], verified=True, verifier=session['orcid']) 
                
                print("this is NEW app:\n", g.get_app(APP['site']))
            elif 'prev_app_site' not in f:
                g.add_app(APP, discoverer=session['orcid']) # submitted as unverified (general user submitted)
            else: 
                return render_template('add-relationship.html', status=status, form=f, topics=topics, types=usage_types.values, 
                    orcid=orcid, role=role, in_session=orcid, essential_variables=essential_variables.values)

            #iterate through the forms dataset list
            upload_datasets_from_form(f, g, APP, session)
            status = "success"

    return render_template('add-relationship.html', status=status, form=f, topics=topics, types=usage_types.values, 
        orcid=orcid, role=role, in_session=orcid, essential_variables=essential_variables.values)

def undo():
    change = None
    #create stack implementation to make undo's 
    if 'changes' in session and len(session['changes'])>0:
        g = graph_db.GraphDB()
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

def bind(flask_app):
    
    flask_app.add_url_rule('/add-relationship', view_func=add_relationship, methods=["GET","POST"])

    flask_app.add_url_rule('/undo', view_func=undo)

    flask_app.add_url_rule('/add-csv', view_func=add_csv, methods=["GET", "POST"])