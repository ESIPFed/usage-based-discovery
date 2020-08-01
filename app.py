from flask import Flask, render_template, request, redirect, url_for, jsonify, json
from flask_wtf import FlaskForm
from wtforms import SelectField
from models import db


app = Flask(__name__)
app.secret_key = 'secret_key'
graph = db()


class Form(FlaskForm):
    topic = SelectField('topic', choices=[])
    application = SelectField('application', choices=[("", "---")])


@app.route('/') #, methods=['GET', 'POST'])
def home():

    topics = graph.nodes.match("Topic")
    return render_template('home.html', topics=topics)




def get_apps(topic):
    query = '''
        match p=(t:Topic)-[r:`relates to`]-(a:Application) 
        WHERE t.name = $topic
        RETURN a.name, a.website, a.publication
        '''
    
    return graph.run(query, topic=topic)



@app.route('/use_cases/<topic>')
def use_cases(topic):
    
    apps = get_apps(topic)
    applications = [app for app in apps]
    
    # return jsonify({'applications' : applications})
    return render_template('use_cases.html', topic=topic, applications=applications)
     



def get_datasets(app):
    query = '''
        match p=(a:Application)-[r:`uses`]-(d:Dataset) 
        WHERE a.name = $app
        RETURN d.identifier, r.conf_level
        '''

    return graph.run(query, app=app)


@app.route('/data/<topic>/<application>')
def data(topic, application):
    
    data = get_datasets(application)
    datasets = [d for d in data]

    # return jsonify({'datasets' : datasets})
    return render_template('data.html', topic=topic, application=application, datasets=datasets)


@app.route('/data/jsonify/<topic>/<application>')
def data_jsonify(topic, application):
    
    data = get_datasets(application)
    datasets = [d[0] for d in data]

    ret = {
        'topic': topic, 
        'application': application, 
        'datasets': datasets
    }

    return jsonify(ret)


if __name__ == '__main__':
    app.run(debug=True)








