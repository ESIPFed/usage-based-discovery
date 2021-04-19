from graph_db import GraphDB

def changeTopics():
    #air to atmospheric aerosols
    #snowfall to snow
    #Soil Moisture to Soil Properties
    #add Air Quaility
    g = GraphDB()
    g.rename_topic('Air', 'Air Quality')

if __name__ == '__main__':
    changeTopics()
