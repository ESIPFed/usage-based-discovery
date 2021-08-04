from flask import session, request, redirect, url_for
import os
import subprocess
import json
from util.s3_functions import s3Functions


def auth():
    '''
    send the user to orcid with our app's client_id
    after the user logs in, they will be redirected to the '/login' route with code
    '''
    if os.environ.get('FLASK_ENV') == 'development':
        # bypass the orcid api
        return redirect(url_for('login'))

    redirect_uri = request.url_root + "/login"
    return redirect("https://orcid.org/oauth/authorize?client_id=" + os.environ.get('CLIENT_ID') +
                    "&response_type=code&scope=/authenticate&redirect_uri=" + redirect_uri)


def login():
    '''
    we get a code from the url that orcid has redirected us back to our site with. 
    that code can be used to access the users orcid data, mainly name and orc-id.
    we do a curl in a subprocess call with the code, to ask orcid for the users orcid data
    we get back the users orcid id, we check if the users orc-id is in our private s3-buckets orcid.json file and assign a role, and orc-id to that session
    '''
    orcid = None
    if os.environ.get('FLASK_ENV') == 'development':  # bypass oauth call
        orcid = os.environ.get('ORCID')
    else:
        code = request.args.get('code')
        inputstr = 'client_id=' + os.environ.get('CLIENT_ID') + \
            '&client_secret=' + os.environ.get('CLIENT_SECRET') + \
            '&grant_type=authorization_code&code=' + code
        output = subprocess.check_output(['curl', '-i', '-L', '-H', 'Accept: application/json',
                                          '--data', inputstr,  'https://orcid.org/oauth/token'], universal_newlines=True)

        ind = output.index('{')
        output = output[ind:]
        output_json = json.loads(output)
        orcid = output_json['orcid']

    s3 = s3Functions()
    data = s3.get_file(os.environ.get('S3_BUCKET'), 'orcid.json')
    data = json.loads(data)
    if orcid in data['supervisor']:
        session['role'] = 'supervisor'
    else:
        session['role'] = 'general'
    session['orcid'] = orcid
    return redirect(url_for('topics'))


def logout():
    del session['orcid']
    del session['role']
    return redirect(request.referrer)


def bind(flask_app):
    flask_app.add_url_rule('/login', view_func=login)

    flask_app.add_url_rule('/logout', view_func=logout)

    flask_app.add_url_rule('/auth', view_func=auth)
