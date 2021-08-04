from flask import request, redirect, session
from util import graph_db

def delete_dataset_relation():
    app_site = request.args.get('app_site')
    doi = request.args.get('doi')
    if 'role' in session and session['role']=='supervisor':
        g = graph_db.GraphDB() 
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

def verify_dataset():
    app_name = request.args.get('app_name')
    doi = request.args.get('doi')
    g = graph_db.GraphDB()
    if 'role' in session and session['role'] == 'supervisor':
        g.verify_relationship(app_name, doi, session['orcid'])
    return redirect(request.referrer)

def add_annotation():
    app_site = request.args.get('app_site')
    doi = request.args.get('doi')
    if request.method == 'POST':
        f = request.form
        g = graph_db.GraphDB()
        g.add_annotation(app_site, doi, f['annotation'])
    return redirect(request.referrer)

def resolve_annotation():
    app_site = request.args.get('app_site')
    doi = request.args.get('doi')
    g = graph_db.GraphDB()
    g.add_annotation(app_site, doi, '')
    return redirect(request.referrer)

def bind(flask_app):
    
    flask_app.add_url_rule('/verify-dataset', view_func=verify_dataset)
    
    flask_app.add_url_rule('/add_annotation', view_func=add_annotation, methods=["GET", "POST"])
   
    flask_app.add_url_rule('/resolve_annotation', view_func=resolve_annotation)

    flask_app.add_url_rule('/delete_dataset_relation', view_func=delete_dataset_relation)