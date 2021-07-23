from flask import request, redirect, session
from util import graph_db

def bind(flask_app):
    
    @flask_app.route('/verify-dataset')
    def verify_dataset():
        app_name = request.args.get('app_name')
        doi = request.args.get('doi')
        g = graph_db.GraphDB()
        if 'role' in session and session['role'] == 'supervisor':
            g.verify_relationship(app_name, doi, session['orcid'])
        return redirect(request.referrer)

    @flask_app.route('/add_annotation', methods=["GET", "POST"])
    def add_annotation():
        app_site = request.args.get('app_site')
        doi = request.args.get('doi')
        if request.method == 'POST':
            f = request.form
            g = graph_db.GraphDB()
            g.add_annotation(app_site, doi, f['annotation'])
        return redirect(request.referrer)

    @flask_app.route('/resolve_annotation')
    def resolve_annotation():
        app_site = request.args.get('app_site')
        doi = request.args.get('doi')
        g = graph_db.GraphDB()
        g.add_annotation(app_site, doi, '')
        return redirect(request.referrer)
