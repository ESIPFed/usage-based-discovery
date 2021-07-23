from util.graph_db import GraphDB
from util.s3_functions import s3Functions
from flask import render_template, request, session, redirect
from util import usage_types
import os, json

def bind(flask_app):    
    
    # Main screen
    @flask_app.route('/apps')
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
            Type = usage_types.values

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
        datasets = []
        if selected_app:
            datasets = g.get_datasets_by_app(selected_app['site'])
            datasets.sort(key=lambda d: d[2]['title'][0], reverse=False)

        #getting temporary images for apps who don't have images
        s3 = s3Functions()
        filename = 'topic/'+topic+'.jpg' 
        if selected_app is not None and selected_app['screenshot'] != 'NA':
            filename = selected_app['screenshot']
        screenshot = s3.create_presigned_url(os.environ.get('S3_BUCKET'), filename)
        
        undo = None
        if 'changes' in session and len(session['changes'])>0:
            undo = json.dumps(session['changes'][-1]['type'])

        return render_template('apps.html',\
            topic=topic, Type=Type, topics=topics, Types=Types, all_types=usage_types.values,\
            string_topic=string_topic, string_type=string_type, apps=topic_apps,\
            app=selected_app, datasets=datasets, screenshot=screenshot, \
            in_session=in_session, trusted_user=trusted_user, undo=undo)

    @flask_app.route('/verify-application')
    def verify_application():
        app_site = request.args.get('app_site')
        g = GraphDB()
        if 'role' in session and session['role'] == 'supervisor':
            g.verify_app(app_site, session['orcid'])
        return redirect(request.referrer)

    @flask_app.route('/delete_application')
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