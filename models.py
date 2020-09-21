from py2neo import Graph, Node, Relationship
import csv
import os

def db():

     
    username = os.environ.get('NEO4J_USERNAME')
    password = os.environ.get('NEO4J_PASSWORD')
    graph = Graph("bolt://hobby-fcaccojbajhegbkelpidkifl.dbs.graphenedb.com:24787", auth=(username, password), secure=True)     

    return graph





