
from flask import request, session, abort

def bind(flask_app):
    
    @flask_app.before_request
    def before_request():
        supervisor_routes = ['/admin', '/delete_application', '/delete_dataset_relation', 
            '/verify-application', '/verify-dataset', '/add-csv', '/download-apps']
        if any(request.path.startswith(s) for s in supervisor_routes):
            if (not 'role' in session) or (not session['role'] == 'supervisor'):
                abort(403)