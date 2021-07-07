from util.graph_db import GraphDB

def rename(old_name, new_name):
    g = GraphDB()
    g.rename_topic(old_name, new_name)
