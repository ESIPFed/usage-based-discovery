from flask import Flask, render_template, request, redirect, url_for, jsonify, json
from flask_wtf import FlaskForm
from wtforms import SelectField
from gremlin import db

# just testing out the commit, to make sure it works for me properly -megan 


app = Flask(__name__)
# app.secret_key = 'secret_key'
graph = db()



# Initial screen
@app.route('/')
def home():
    topics = graph.V().hasLabel('application').values('topic').toSet()
    return render_template('init.html', topics=topics)


@app.route('/about')
def about():
    return render_template('about.html')

'''
@app.route('/')
def home():
    topics = graph.V().hasLabel('application').values('topic').toSet()
    

    # query for all applications and put in a list
    apps = graph.V().hasLabel('application').elementMap().toList()
    for a in apps:
        print(a)
    datasets = graph.V().hasLabel('dataset').elementMap().toList()

    return render_template('index.html', topics=topics, apps=apps, datasets=datasets)
'''




#Main screen 
@app.route('/<topic>/<app>') 
def main(topic, app): 

    # query for all topic property values and put into list
    topics = graph.V().hasLabel('application').values('topic').toSet()
    
    ''' don't need anymore because there will always be a topic selected
    # query for all applications and put in a list
    apps = graph.V().hasLabel('application').elementMap().toList()
    for a in relapps:
        print(a)
    '''
    
    # query only for application relating to specified topic
    relapps = graph.V().has('application', 'topic', topic).elementMap().toList()
    
    
    # query for single application (vertex) with name specified by parameter 
    if(app == 'all'):
        appsel = None

        # query for datasets related to relapps[0]
        apps = graph.V().has('application', 'topic', topic)
        datasets = apps.out().elementMap().toList()

    else:
        appsel = graph.V().has('application', 'name', app).elementMap().toList()

        # query for all datasets relating to specified application
        selected = graph.V().has('application', 'name', app)
        datasets = selected.out().elementMap().toList()
        '''for d in datasets: 
            print(d)
        # datasets = graph.V().hasLabel('dataset').elementMap().toList()'''


    return render_template('index.html', topic=topic, \
        topics=topics, apps=relapps, app=appsel, datasets=datasets)





if __name__ == '__main__':
    app.run(debug=True)






'''

class Form(FlaskForm):
    choices = ['Application Topic', 'Floods', 'Wildfires', 'Landslides']
    dropdown = SelectField('topic', choices=choices, default=0)


@app.route('/') #, methods=['GET', 'POST'])
def home():

    topics = graph.nodes.match("Topic")
    return render_template('home.html', topics=topics)




def get_apps(topic):
    query = ''
        match p=(t:Topic)-[r:`relates to`]-(a:Application) 
        WHERE t.name = $topic
        RETURN a.name, a.website, a.publication
        ''
    
    return graph.run(query, topic=topic)



@app.route('/use_cases/<topic>')
def use_cases(topic):
    
    apps = get_apps(topic)
    applications = [app for app in apps]
    
    # return jsonify({'applications' : applications})
    return render_template('use_cases.html', topic=topic, applications=applications)
     



def get_datasets(app):
    query = ''
        match p=(a:Application)-[r:`uses`]-(d:Dataset) 
        WHERE a.name = $app
        RETURN d.identifier, r.conf_level
        ''

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

'''
