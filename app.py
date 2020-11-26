from flask import Flask, render_template 
from gremlin import db

app = Flask(__name__)
graph = db()


# Initial screen
@app.route('/')
def home():
    topics = graph.V().hasLabel('application').values('topic').toSet()
    return render_template('init.html', topics=topics)


@app.route('/about')
def about():
    return render_template('about.html')



# Main screen 
@app.route('/<topic>/<app>') 
def main(topic, app): 

    # query for all topic property values and put into list
    topics = graph.V().hasLabel('application').values('topic').toSet()
  
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
        

    return render_template('index.html', topic=topic, \
        topics=topics, apps=relapps, app=appsel, datasets=datasets)


if __name__ == '__main__':
    app.run(debug=True)




'''
Previous home route

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

